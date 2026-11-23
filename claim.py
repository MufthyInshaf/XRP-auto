import os, random, re, time
from playwright.sync_api import sync_playwright

USER = os.environ["FE_USER"]
PASS = os.environ["FE_PASS"]
BASE = "https://faucetearner.org"
RUN_LIMIT = 5 * 3600 + 45 * 60  # GitHub job limit 6h; exit before it
START = time.time()

def pause(a=1.5, b=4):
    time.sleep(random.uniform(a, b))

def login(page):
    page.goto(BASE + "/login.php")      # TODO: confirm real login URL
    pause()
    page.fill('input[type="text"], input[name*="user" i], input[name*="email" i]', USER)
    pause(0.5, 1.5)
    page.fill('input[type="password"]', PASS)
    pause(0.5, 1.5)
    page.click('button:has-text("Login")')
    page.wait_for_load_state("networkidle")

def claim(page):
    page.goto(BASE + "/faucet.php")     # TODO: confirm real faucet URL
    pause()
    btn = page.locator('button:has-text("Claim Now")')
    if btn.count() and btn.first.is_enabled():
        btn.first.hover(); pause(0.5, 1.5)
        btn.first.click()
        print(time.strftime("%H:%M:%S"), "claimed", flush=True)
        pause(3, 5)
    else:
        print(time.strftime("%H:%M:%S"), "not ready", flush=True)

def seconds_left(page):
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
            wait = 120
            try: login(page)
            except Exception: pass
        time.sleep(max(wait, 30))
