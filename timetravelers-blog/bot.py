"""
Admin Bot - Simulates an admin visiting blog posts with a flag cookie.
Uses Playwright for headless browsing so JavaScript actually executes.
This is what makes the XSS exploitable.
"""

import asyncio
import os
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright

bot_app = FastAPI(title="Admin Bot", docs_url=None)

FLAG = os.environ.get("FLAG", "HIT{x55_t1m3_tr4v3l_1s_d4ng3r0us}")
APP_URL = os.environ.get("APP_URL", "http://web:8000")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "s3cr3t_4dm1n_t0k3n_d0_n0t_l34k")

# Rate limiting
visit_lock = asyncio.Lock()
last_visit = 0
COOLDOWN = 5  # seconds


@bot_app.post("/visit")
async def visit_page(url: str = Form(...)):
    """
    Make the admin bot visit a URL.
    The bot has the flag stored as a cookie.
    """
    global last_visit

    # Basic validation: only allow visiting the blog
    allowed_prefixes = [APP_URL, "http://localhost", "http://web", "http://127.0.0.1"]
    if not any(url.startswith(prefix) for prefix in allowed_prefixes):
        return JSONResponse(
            {"error": "The admin bot can only visit the blog."},
            status_code=400,
        )

    # Rate limiting
    now = asyncio.get_event_loop().time()
    if now - last_visit < COOLDOWN:
        return JSONResponse(
            {"error": f"Please wait {COOLDOWN}s between visits."},
            status_code=429,
        )

    async with visit_lock:
        last_visit = asyncio.get_event_loop().time()

        try:
            # Extract domain from the URL for cookie assignment
            from urllib.parse import urlparse

            parsed = urlparse(url)
            cookie_domain = parsed.hostname  # "web", "localhost", etc.

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                context = await browser.new_context()

                # Set the flag cookie on the correct domain
                await context.add_cookies(
                    [
                        {
                            "name": "flag",
                            "value": FLAG,
                            "domain": cookie_domain,
                            "path": "/",
                        },
                        {
                            "name": "session",
                            "value": ADMIN_SECRET,
                            "domain": cookie_domain,
                            "path": "/",
                        },
                    ]
                )

                page = await context.new_page()

                # Visit the page (JS will execute, triggering the XSS)
                await page.goto(url, timeout=10000)
                await page.wait_for_timeout(3000)

                await browser.close()

            return JSONResponse(
                {"success": True, "message": "Admin reviewed the page."}
            )

        except Exception as e:
            return JSONResponse(
                {"error": f"Bot error: {str(e)}"},
                status_code=500,
            )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(bot_app, host="0.0.0.0", port=3000)
