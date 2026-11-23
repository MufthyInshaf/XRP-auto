import os, random, re, time
from playwright.sync_api import sync_playwright

USER = os.environ["FE_USER"]
PASS = os.environ["FE_PASS"]
BASE = "https://faucetearner.org/"
RUN_LIMIT = 5 * 3600 + 45 * 60
START = time.time()

def pause(a=1.5, b=4):
    time.sleep(random.uniform(a, b))

def diag(page, note=""):
    # login தகவல் எதுவும் print ஆகாது
    print("DIAG", note, "| URL:", page.url, "| TITLE:", page.title(), flush=True)
    print("INPUTS:", page.eval_on_selector_all(
        "input", "els => els.map(e => [e.type, e.name, e.id, e.placeholder])"), flush=True)
    print("LINKS/BUTTONS:", page.eval_on_selector_all(
        "button, a", "els => els.map(e => e.innerText.trim()).filter(t => t).slice(0, 30)"), flush=True)
    print("TEXT:", page.inner_text("body")[:400].replace("\n", " | "), flush=True)

def login(page):
    page.goto(BASE, wait_until="networkidle")
    pause()
    page.locator('a:visible:has-text("Login")').first.click()
    page.wait_for_load_state("networkidle")
    pause()
    try:
        page.wait_for_selector('input[type="password"]', timeout=15000)
    except Exception:
        diag(page, "login form not found")
        raise
    page.locator('input:not([type="password"]):not([type="hidden"])').first.fill(USER)
    pause(0.5, 1.5)
    page.locator('input[type="password"]').first.fill(PASS)
    pause(0.5, 1.5)
    page.locator('button:visible:has-text("Login"), input[type="submit"]').first.click()
    page.wait_for_load_state("networkidle")
    pause(2, 4)
    if page.locator('input[type="password"]').count():
        diag(page, "still on login page (wrong password or blocked)")
        raise RuntimeError("login failed")
    print("login ok", flush=True)

def open_faucet(page):
    link = page.locator('a:visible:has-text("Faucet")').first
    link.click()
    page.wait_for_load_state("networkidle")
    pause()

def claim(page):
    open_faucet(page)
    btn = page.locator('button:visible:has-text("Claim Now"), a:visible:has-text("Claim Now")')
    if btn.count() and btn.first.is_enabled():
        btn.first.hover(); pause(0.5, 1.5)
        btn.first.click()
        print(time.strftime("%H:%M:%S"), "claimed", flush=True)
        pause(3, 5)
    else:
        print(time.strftime("%H:%M:%S"), "not ready", flush=True)

def seconds_left(page):
    open_faucet(page)
    m = re.search(r"(\d{2}):(\d{2})", page.inner_text("body"))
    return int(m[1]) * 60 + int(m[2]) if m else 600

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 412, "height": 915},
        user_agent="Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                   "Chrome/124.0 Mobile Safari/537.36")
    page = ctx.new_page()
    login(page)
    while time.time() - START < RUN_LIMIT:
        try:
            claim(page)
            wait = seconds_left(page) + random.randint(5, 40)
        except Exception as e:
            print("error:", type(e).__name__, flush=True)
            try: diag(page, "claim error")
            except Exception: pass
            wait = 120
            try: login(page)
            except Exception: pass
        time.sleep(max(wait, 30))
