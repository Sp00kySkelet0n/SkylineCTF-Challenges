"""
HackInTime - Challenge 04 - Paradox Machine
Difficulty: Hard
Vulnerability: Server-Side Template Injection (SSTI) -> RCE

A "temporal simulation engine" that lets users input temporal coordinates and parameters. The input is rendered through Jinja2 without sandboxing, allowing SSTI. Players must escalate from template injection to reading a flag file on the server.
"""

from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
import os
import hashlib
import secrets
import sqlite3
from jinja2 import Environment, BaseLoader

app = FastAPI(title="Paradox Machine", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

_BASE = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.environ.get("DATABASE", os.path.join(_BASE, "/tmp/paradox.db"))
FLAG_FILE = os.environ.get("FLAG_FILE", os.path.join(_BASE, "flag.txt"))
FLAG = os.environ.get("FLAG", "HIT{sst1_p4r4d0x_rce_t1m3l1n3_br34ch}")

# In-memory sessions
sessions: dict[str, dict] = {}


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            rank TEXT DEFAULT 'cadet'
        );
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operator_id INTEGER NOT NULL,
            coordinates TEXT NOT NULL,
            parameters TEXT NOT NULL,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operator_id) REFERENCES operators(id)
        );
    """
    )

    c.execute("SELECT COUNT(*) FROM operators")
    if c.fetchone()[0] == 0:
        operators = [
            (
                "admin",
                hashlib.sha256("Parad0x_Mach1n3_2147!".encode()).hexdigest(),
                "Dr. Paradox",
                "commander",
            ),
            (
                "operator",
                hashlib.sha256("operator".encode()).hexdigest(),
                "Operator Delta-7",
                "cadet",
            ),
        ]
        c.executemany(
            "INSERT INTO operators (username, password_hash, full_name, rank) VALUES (?,?,?,?)",
            operators,
        )

    conn.commit()
    conn.close()

    # Write flag to file (for RCE-based retrieval)
    with open(FLAG_FILE, "w") as f:
        f.write(FLAG)


@app.on_event("startup")
async def startup():
    init_db()


# ─── Session helpers ────────────────────────────────────────────────


def get_session(session_id: Optional[str]) -> Optional[dict]:
    if session_id and session_id in sessions:
        return sessions[session_id]
    return None


def create_session(user: dict) -> str:
    sid = secrets.token_hex(32)
    sessions[sid] = {
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "rank": user["rank"],
    }
    return sid


# ─── Auth ───────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if user:
        return RedirectResponse(url="/simulator", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user = conn.execute(
        "SELECT * FROM operators WHERE username = ? AND password_hash = ?",
        (username, pw_hash),
    ).fetchone()
    conn.close()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Access denied. Invalid temporal credentials.",
            },
        )

    sid = create_session(dict(user))
    resp = RedirectResponse(url="/simulator", status_code=303)
    resp.set_cookie(key="session", value=sid, httponly=True)
    return resp


@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    if session and session in sessions:
        del sessions[session]
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie("session")
    return resp


# ─── Simulator (SSTI vulnerable) ───────────────────────────────────


@app.get("/simulator", response_class=HTMLResponse)
async def simulator_page(request: Request, session: Optional[str] = Cookie(None)):
    user = get_session(session)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    # Load past simulations
    conn = get_db()
    sims = conn.execute(
        "SELECT * FROM simulations WHERE operator_id = ? ORDER BY created_at DESC LIMIT 10",
        (user["user_id"],),
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        "simulator.html",
        {"request": request, "user": user, "simulations": sims},
    )


@app.post("/simulate", response_class=HTMLResponse)
async def run_simulation(
    request: Request,
    session: Optional[str] = Cookie(None),
    coordinates: str = Form(...),
    parameters: str = Form(""),
):
    user = get_session(session)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    # The "simulation engine" renders coordinates through Jinja2
    # This is the SSTI vulnerability
    try:
        env = Environment(loader=BaseLoader())
        # VULNERABLE: user input is treated as a Jinja2 template
        template_str = f"""
        <div class="sim-output">
            <div class="output-header">SIMULATION RESULT</div>
            <div class="output-field">
                <span class="field-label">Temporal Coordinates:</span>
                <span class="field-value">{coordinates}</span>
            </div>
            <div class="output-field">
                <span class="field-label">Parameters:</span>
                <span class="field-value">{parameters}</span>
            </div>
            <div class="output-field">
                <span class="field-label">Status:</span>
                <span class="field-value status-ok">SIMULATION COMPLETE</span>
            </div>
            <div class="output-field">
                <span class="field-label">Paradox Index:</span>
                <span class="field-value">0.0042 (within acceptable bounds)</span>
            </div>
        </div>
        """
        rendered = env.from_string(template_str).render()
    except Exception as e:
        rendered = f"""
        <div class="sim-output sim-error">
            <div class="output-header">⚠ TEMPORAL ANOMALY DETECTED</div>
            <div class="output-field">
                <span class="field-label">Error:</span>
                <span class="field-value">{str(e)}</span>
            </div>
            <div class="output-field">
                <span class="field-label">Input:</span>
                <span class="field-value">{coordinates[:100]}</span>
            </div>
        </div>
        """

    # Save simulation to DB
    conn = get_db()
    conn.execute(
        "INSERT INTO simulations (operator_id, coordinates, parameters, result) VALUES (?, ?, ?, ?)",
        (user["user_id"], coordinates[:200], parameters[:200], "completed"),
    )
    conn.commit()

    sims = conn.execute(
        "SELECT * FROM simulations WHERE operator_id = ? ORDER BY created_at DESC LIMIT 10",
        (user["user_id"],),
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        "simulator.html",
        {
            "request": request,
            "user": user,
            "simulations": sims,
            "result": rendered,
        },
    )


# ─── Easter egg: source hint ───────────────────────────────────────


@app.get("/robots.txt")
async def robots():
    return HTMLResponse(
        content="User-agent: *\n"
        "Disallow: /simulator\n"
        "Disallow: /flag.txt\n"
        "Media-Type: text/plain",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
