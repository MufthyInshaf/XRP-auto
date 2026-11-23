from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(
        viewport={"width": 412, "height": 915},
        user_agent="Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                   "Chrome/124.0 Mobile Safari/537.36")
    page = ctx.new_page()
    r = page.goto("https://faucetearner.org/", wait_until="networkidle")
    print("STATUS:", r.status if r else None)
    print("URL:", page.url)
    print("TITLE:", page.title())
    print("INPUTS:", page.eval_on_selector_all(
        "input", "els => els.map(e => [e.type, e.name, e.id, e.placeholder])"))
    print("BUTTONS:", page.eval_on_selector_all(
        "button, a", "els => els.map(e => e.innerText.trim()).filter(t => t).slice(0, 40)"))
    print("TEXT:", page.inner_text("body")[:600])
    b.close()
