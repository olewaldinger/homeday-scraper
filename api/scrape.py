from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os
import logging

# Logging konfigurieren für bessere Fehlermeldungen
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/api/scrape")
def scrape():
    address = request.args.get("address", "")
    if not address:
        return jsonify({"error": "Address missing"}), 400

    search_address = address.lower().replace(" ", "-")
    url = f"https://www.homeday.de/de/preisatlas/{search_address}"

    try:
        with sync_playwright() as p:
            logger.info(f"Starting browser for URL: {url}")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            logger.info(f"Navigating to {url}")
            page.goto(url, timeout=120000)  # Erhöht auf 120 Sekunden
            page.wait_for_load_state("networkidle")  # Warte, bis die Seite vollständig geladen ist
            page.wait_for_timeout(5000)  # Zusätzliche 5 Sekunden Puffer

            logger.info("Searching for price elements")
            elements = page.query_selector_all("p.price-block__price__average")
            prices = [el.inner_text() for el in elements if el]

            browser.close()
            logger.info(f"Found prices: {prices}")

            if len(prices) < 2:
                return jsonify({"error": "Nicht alle Preise gefunden"}), 404

            return jsonify({
                "hauspreis": prices[0],
                "wohnungspreis": prices[1]
            }), 200

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500