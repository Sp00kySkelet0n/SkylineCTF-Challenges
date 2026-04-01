"""
HackInTime - Challenge 01: TimeTraveler's Blog
Difficulty: Easy
Vulnerability: Stored XSS → Cookie Stealing

A retro blog about time travel where users can post comments.
The comments are rendered without sanitization, allowing stored XSS.
The flag is hidden in an admin cookie that visits the page periodically.
"""

from fastapi import FastAPI, Request, Response, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
import sqlite3
import os
import time
import threading
import httpx

app = FastAPI(title="TimeTraveler's Blog", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Disable Jinja2 autoescaping intentionally (this is the vulnerability)
templates.env.autoescape = False

DATABASE = "/tmp/blog.db"
FLAG = os.environ.get("FLAG", "HIT{x55_t1m3_tr4v3l_1s_d4ng3r0us}")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "s3cr3t_4dm1n_t0k3n_d0_n0t_l34k")
BOT_URL = os.environ.get("BOT_URL", "http://localhost:8000")


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with tables and seed data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT DEFAULT 'Admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );
    """)

    # Seed blog posts if empty
    cursor.execute("SELECT COUNT(*) FROM posts")
    if cursor.fetchone()[0] == 0:
        seed_posts = [
            (
                "Welcome to the Time Traveler's Blog",
                "Greetings, fellow chronauts! This blog documents our journeys "
                "through the temporal streams. Feel free to leave comments about "
                "your own time travel experiences. Remember: don't create paradoxes!",
                "Dr. Chronos",
            ),
            (
                "My Trip to 1985",
                "Just got back from 1985. The music was amazing, the fashion was... "
                "questionable. Pro tip: if you visit the 80s, bring your own coffee. "
                "Trust me on this one.",
                "TemporalTourist",
            ),
            (
                "WARNING: Temporal Anomaly Detected",
                "Our sensors have detected unusual activity in the comment system. "
                "The admin bot regularly checks all comments for suspicious content. "
                "If you notice anything strange, report it immediately.",
                "Dr. Chronos",
            ),
        ]
        cursor.executemany(
            "INSERT INTO posts (title, content, author) VALUES (?, ?, ?)",
            seed_posts,
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup():
    init_db()


# ─── Pages ──────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db()
    posts = conn.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    conn.close()
    return templates.TemplateResponse(
        "index.html", {"request": request, "posts": posts}
    )


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(request: Request, post_id: int):
    conn = get_db()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC",
        (post_id,),
    ).fetchall()
    conn.close()

    if not post:
        return HTMLResponse("<h1>Post not found</h1>", status_code=404)

    return templates.TemplateResponse(
        "post.html", {"request": request, "post": post, "comments": comments}
    )


@app.post("/post/{post_id}/comment")
async def add_comment(
    post_id: int, username: str = Form(...), content: str = Form(...)
):
    """
    Add a comment to a post.
    VULNERABILITY: No input sanitization — content is stored raw and rendered
    without escaping, allowing stored XSS.
    """
    conn = get_db()
    conn.execute(
        "INSERT INTO comments (post_id, username, content) VALUES (?, ?, ?)",
        (post_id, username, content),
    )
    conn.commit()
    conn.close()

    # Trigger the admin bot to visit the page (simulates admin reviewing comments)
    threading.Thread(target=admin_bot_visit, args=(post_id,), daemon=True).start()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)


# ─── Admin Bot ──────────────────────────────────────────────────────


def admin_bot_visit(post_id: int):
    """
    Triggers the Playwright admin bot to visit the page.
    The bot has the flag in its cookies and executes JS (making XSS exploitable).
    """
    time.sleep(2)
    try:
        bot_api = os.environ.get("BOT_API_URL", "http://localhost:3000")
        httpx.post(
            f"{bot_api}/visit",
            data={"url": f"{BOT_URL}/post/{post_id}"},
            timeout=15,
        )
    except Exception as e:
        print(f"[BOT] Error triggering admin bot: {e}")


# ─── Webhook Receiver (for catching exfiltrated cookies) ────────────


@app.get("/webhook", response_class=HTMLResponse)
async def webhook(request: Request, data: Optional[str] = None):
    """
    Endpoint that can receive exfiltrated data.
    In a real CTF this would be the attacker's server (e.g., RequestBin).
    This is included for self-contained testing.
    """
    if data:
        print(f"\n{'=' * 60}")
        print(f"[WEBHOOK] Received exfiltrated data:")
        print(f"  {data}")
        print(f"{'=' * 60}\n")
    return HTMLResponse(
        f"<html><body><h3>Webhook received</h3><p>Data: {data}</p></body></html>"
    )


# ─── Flag Check (for CTF platform integration) ─────────────────────


@app.post("/check-flag")
async def check_flag(flag: str = Form(...)):
    if flag.strip() == FLAG:
        return {"correct": True, "message": "🎉 Congratulations, time traveler!"}
    return {
        "correct": False,
        "message": "Wrong flag. Keep searching the timeline...",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
