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
    print("DIAG", note, "| URL:", page.url, flush=True)
    print("BUTTONS:", page.eval_on_selector_all(
        "button, a", "els => els.map(e => e.innerText.trim()).filter(t => t).slice(0, 25)"), flush=True)
    print("TEXT:", page.inner_text("body")[:500].replace("\n", " | "), flush=True)

def login(page):
    page.goto(BASE + "login.php", wait_until="domcontentloaded")
    pause(2, 4)
    page.wait_for_selector('input[type="password"]', timeout=20000)
    page.locator('input:not([type="password"]):not([type="hidden"])').first.fill(USER)
    pause(0.5, 1.5)
    page.locator('input[type="password"]').first.fill(PASS)
    pause(0.5, 1.5)
    page.locator('button:visible:has-text("Login"), input[type="submit"]').first.click()
    page.wait_for_url("**/dashboard.php", timeout=20000)
    print("login ok", flush=True)

def seconds_left(page):
    m = re.search(r"Next Claim In\s*(\d{2}):(\d{2})", page.inner_text("body"))
    if m:
        s = int(m[1]) * 60 + int(m[2])
        if 0 < s <= 700:
            return s
    return 600

def claim(page):
    page.goto(BASE + "faucet.php", wait_until="domcontentloaded")
    pause(3, 5)
    if "login" in page.url:
        raise RuntimeError("logged out")
    btn = page.locator('button:visible:has-text("Claim Now"), a:visible:has-text("Claim Now")')
    if btn.count() and btn.first.is_enabled():
        btn.first.hover(); pause(0.5, 1.5)
        btn.first.click()
        print(time.strftime("%H:%M:%S"), "CLICKED Claim Now", flush=True)
        pause(5, 8)
        print("after click:", page.inner_text("body")[:200].replace("\n", " | "), flush=True)
    else:
        print(time.strftime("%H:%M:%S"), "button not ready", flush=True)
        diag(page, "no claim button")
    return seconds_left(page)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 412, "height": 915},
        user_agent="Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                   "Chrome/124.0 Mobile Safari/537.36")
    page = ctx.new_page()
    page.set_default_timeout(25000)
    login(page)
    while time.time() - START < RUN_LIMIT:
        try:
            wait = claim(page) + random.randint(10, 60)
        except Exception as e:
            print("error:", type(e).__name__, str(e)[:150], flush=True)
            wait = 90
            try: login(page)
            except Exception as e2: print("relogin failed:", type(e2).__name__, flush=True)
        print("sleep", wait, "sec", flush=True)
        time.sleep(max(wait, 30))
