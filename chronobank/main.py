"""
HackInTime - Challenge 02: Chronobank
Difficulty: Medium
Vulnerabilities:
  1. SQL Injection on login (authentication bypass)
  2. IDOR on account endpoint (access other users' data)

A futuristic banking app for time travelers. Players must bypass login
via SQLi, then exploit an IDOR to access the admin's secret vault
containing the flag.
"""

from fastapi import FastAPI, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
import sqlite3
import hashlib
import os
import secrets

app = FastAPI(title="Chronobank", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE = "/tmp/chronobank.db"
FLAG = os.environ.get("FLAG", "HIT{1d0r_4nd_sql1_t1m3_h31st}")
SECRET_KEY = os.environ.get("SECRET_KEY", "chronobank_secret_key_2147")

# In-memory session store
sessions: dict[str, dict] = {}


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            balance REAL DEFAULT 0,
            currency TEXT DEFAULT 'TC',
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            secret_name TEXT NOT NULL,
            secret_value TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # Seed data if empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        users = [
            ("admin", hash_password("T3mp0r4l_S3cur1ty_2147!"), "Dr. Chronos", "admin"),
            ("jdoe", hash_password("password123"), "John Doe", "user"),
            ("msmith", hash_password("temporal2024"), "Mary Smith", "user"),
            ("traveler42", hash_password("backto1985"), "Anonymous Traveler", "user"),
        ]
        c.executemany(
            "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
            users,
        )

        accounts = [
            # admin accounts (user_id=1)
            (1, "Temporal Vault Prime", "CHRONO-0001-ADMIN", 9999999.99, "TC"),
            (1, "Secret Operations Fund", "CHRONO-0002-ADMIN", 1337000.00, "TC"),
            # jdoe accounts (user_id=2)
            (2, "Savings Account", "CHRONO-1001-JDOE", 4250.50, "TC"),
            (2, "Travel Fund", "CHRONO-1002-JDOE", 890.00, "TC"),
            # msmith (user_id=3)
            (3, "Primary Account", "CHRONO-2001-MSMITH", 12750.00, "TC"),
            # traveler42 (user_id=4)
            (4, "Emergency Fund", "CHRONO-3001-T42", 320.75, "TC"),
        ]
        c.executemany(
            "INSERT INTO accounts (user_id, account_name, account_number, balance, currency) VALUES (?, ?, ?, ?, ?)",
            accounts,
        )

        transactions = [
            (1, "Temporal research grant", 500000.00, "2147-01-15"),
            (1, "Classified operation funding", 1337000.00, "2147-02-20"),
            (3, "Salary deposit - Temporal Inc.", 6500.00, "2147-03-01"),
            (3, "Rent payment", -2200.00, "2147-03-05"),
            (4, "Time travel ticket refund", 320.75, "2147-03-10"),
            (5, "Freelance temporal consulting", 12750.00, "2147-03-12"),
            (6, "Emergency time jump deposit", 320.75, "2147-03-15"),
        ]
        c.executemany(
            "INSERT INTO transactions (account_id, description, amount, date) VALUES (?, ?, ?, ?)",
            transactions,
        )

        # Admin vault contains the flag
        vault_entries = [
            (1, "Temporal Access Code", FLAG),
            (1, "Emergency Override", "OVERRIDE-7742-ALPHA"),
            (2, "Personal Note", "Remember to buy milk"),
        ]
        c.executemany(
            "INSERT INTO vault (user_id, secret_name, secret_value) VALUES (?, ?, ?)",
            vault_entries,
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup():
    init_db()


# ─── Helpers ────────────────────────────────────────────────────────

def get_session(session_id: Optional[str]) -> Optional[dict]:
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None


def create_session(user: dict) -> str:
    session_id = secrets.token_hex(32)
    sessions[session_id] = {
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
    }
    return session_id


# ─── Pages ──────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    hashed = hash_password(password)

    # VULNERABLE QUERY — string concatenation instead of parameterized
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}'"

    try:
        user = conn.execute(query).fetchone()
    except Exception as e:
        conn.close()
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"Database error: {e}"},
        )

    conn.close()

    if user:
        session_id = create_session(dict(user))
        resp = RedirectResponse(url="/dashboard", status_code=303)
        resp.set_cookie(key="session", value=session_id, httponly=True)
        return resp

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials. Access denied."},
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    accounts = conn.execute(
        "SELECT * FROM accounts WHERE user_id = ?", (user["user_id"],)
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "accounts": accounts},
    )


@app.get("/account/{account_id}", response_class=HTMLResponse)
async def view_account(request: Request, account_id: int, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()

    # VULNERABLE: No check that account belongs to the current user
    account = conn.execute(
        "SELECT a.*, u.full_name as owner_name FROM accounts a JOIN users u ON a.user_id = u.id WHERE a.id = ?",
        (account_id,),
    ).fetchone()

    transactions = []
    if account:
        transactions = conn.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY date DESC",
            (account_id,),
        ).fetchall()

    conn.close()

    if not account:
        return HTMLResponse("<h1>Account not found</h1>", status_code=404)

    return templates.TemplateResponse(
        "account.html",
        {"request": request, "user": user, "account": account, "transactions": transactions},
    )


@app.get("/vault", response_class=HTMLResponse)
async def view_vault(request: Request, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    conn = get_db()
    vault_entries = conn.execute(
        "SELECT * FROM vault WHERE user_id = ?", (user["user_id"],)
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        "vault.html",
        {"request": request, "user": user, "vault_entries": vault_entries},
    )


@app.get("/api/vault/{user_id}")
async def api_vault(user_id: int, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if not user:
        return {"error": "Not authenticated"}

    # VULNERABLE: No check that user_id matches the logged-in user
    conn = get_db()
    entries = conn.execute(
        "SELECT id, secret_name, secret_value FROM vault WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    conn.close()

    return {"user_id": user_id, "entries": [dict(e) for e in entries]}


@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    if session and session in sessions:
        del sessions[session]
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session")
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
