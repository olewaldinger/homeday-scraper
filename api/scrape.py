from playwright.sync_api import sync_playwright

def handler(request):
    try:
        address = request.query.get("address", "")
        if not address:
            return {
                "statusCode": 400,
                "body": "Address missing"
            }

        search_address = address.lower().replace(" ", "-")
        url = f"https://www.homeday.de/de/preisatlas/{search_address}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)

            content = page.content()
            if "Preisspanne" not in content:
                return {
                    "statusCode": 404,
                    "body": "Preisspanne nicht gefunden"
                }

            el = page.query_selector("h3:has-text('Preisspanne')")
            text = el.inner_text() if el else "Kein Preis gefunden"

        return {
            "statusCode": 200,
            "body": text
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
