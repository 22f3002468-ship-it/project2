from playwright.sync_api import sync_playwright


def render_page_html(url: str, timeout_ms: int = 30000) -> str:
    """
    Uses Playwright to open a JS-heavy page and return the final HTML.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            # Small extra wait for late JS
            page.wait_for_timeout(1000)
            html = page.content()
        finally:
            browser.close()
    return html
