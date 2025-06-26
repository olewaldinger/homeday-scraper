from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

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
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)

            elements = page.query_selector_all("p.price-block__price__average")
            prices = [el.inner_text() for el in elements if el]

            browser.close()

            if len(prices) < 2:
                return jsonify({"error": "Nicht alle Preise gefunden"}), 404

            return jsonify({
                "hauspreis": prices[0],
                "wohnungspreis": prices[1]
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Nur lokal:
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

