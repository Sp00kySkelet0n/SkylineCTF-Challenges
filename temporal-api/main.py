"""
HackInTime - Challenge 03: Temporal API
Difficulty: Medium+
Vulnerabilities:
  1. JWT signed with weak secret (brute-forceable)
  2. Algorithm confusion: server accepts "none" algorithm
  3. Broken access control: role claim in JWT controls access
  4. Hidden admin endpoint discoverable via API docs leak

Players must forge a JWT token with role=admin to access
the restricted /api/v1/temporal/classified endpoint containing the flag.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import jwt
import hashlib
import sqlite3
import os
import time
import json
from datetime import datetime, timedelta

# ─── Config ─────────────────────────────────────────────────────────

FLAG = os.environ.get("FLAG", "HIT{jwt_n0n3_4lg0_t1m3_tr4v3l_cl34r4nc3}")
JWT_SECRET = os.environ.get("JWT_SECRET", "time")  # Intentionally weak secret!
DATABASE = "/tmp/temporal_api.db"

app = FastAPI(
    title="Temporal Research Institute - API",
    description="Internal API for temporal research operations. Clearance required.",
    version="3.7.1",
    # Swagger UI intentionally enabled (information disclosure)
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Database ───────────────────────────────────────────────────────


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS researchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'researcher',
            clearance_level INTEGER DEFAULT 1,
            department TEXT DEFAULT 'General Research'
        );
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codename TEXT NOT NULL,
            destination_year INTEGER NOT NULL,
            status TEXT DEFAULT 'planned',
            clearance_required INTEGER DEFAULT 1,
            briefing TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT
        );
    """)

    c.execute("SELECT COUNT(*) FROM researchers")
    if c.fetchone()[0] == 0:
        researchers = [
            (
                "admin",
                hashlib.sha256("T3mp0r4l_Adm1n_2147!".encode()).hexdigest(),
                "Dr. Chronos",
                "admin",
                5,
                "Temporal Command",
            ),
            (
                "jmartin",
                hashlib.sha256("researcher123".encode()).hexdigest(),
                "Dr. Julia Martin",
                "researcher",
                2,
                "Quantum Mechanics",
            ),
            (
                "klee",
                hashlib.sha256("temporalphysics".encode()).hexdigest(),
                "Prof. Kevin Lee",
                "researcher",
                1,
                "Temporal Physics",
            ),
            (
                "guest",
                hashlib.sha256("guest".encode()).hexdigest(),
                "Guest Visitor",
                "guest",
                0,
                "Visitor",
            ),
        ]
        c.executemany(
            "INSERT INTO researchers (username, password_hash, full_name, role, clearance_level, department) VALUES (?,?,?,?,?,?)",
            researchers,
        )

        missions = [
            (
                "OPERATION PARADOX",
                1945,
                "completed",
                1,
                "Historical observation mission to WWII-era Europe. Standard temporal protocols apply.",
            ),
            (
                "PROJECT RENAISSANCE",
                1503,
                "active",
                2,
                "Cultural observation of Renaissance Italy. Interact minimally with locals.",
            ),
            (
                "MISSION APOLLO",
                1969,
                "planned",
                1,
                "Verify historical accuracy of Apollo 11 moon landing. Photography permitted.",
            ),
            (
                "OMEGA PROTOCOL",
                2089,
                "classified",
                5,
                "CLASSIFIED - ACCESS RESTRICTED TO CLEARANCE LEVEL 5 - "
                "Contains temporal coordinates for the origin event. "
                f"Authorization code: {FLAG}",
            ),
        ]
        c.executemany(
            "INSERT INTO missions (codename, destination_year, status, clearance_required, briefing) VALUES (?,?,?,?,?)",
            missions,
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
async def startup():
    init_db()


# ─── JWT Helpers ────────────────────────────────────────────────────


def create_token(user: dict) -> str:
    """Create a JWT token with user claims."""
    payload = {
        "sub": user["username"],
        "name": user["full_name"],
        "role": user["role"],
        "clearance": user["clearance_level"],
        "department": user["department"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    """
    VULNERABILITY 1: Algorithm confusion
    - The server decodes with algorithms=["HS256", "none"]
    - This means a token with alg:"none" and no signature is accepted!

    VULNERABILITY 2: Weak secret
    - JWT_SECRET is "time" - easily brute-forceable with tools like hashcat or jwt_tool
    """
    try:
        # VULNERABLE: accepts "none" algorithm
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256", "none"],
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(request: Request) -> dict | None:
    """Extract and verify JWT from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    return verify_token(token)


def require_auth(request: Request):
    """Dependency: require valid JWT."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(
            {"error": "Missing Authorization header. Use: Bearer <token>"},
            status_code=401,
        )
    token = auth[7:]
    user = verify_token(token)
    if not user:
        return JSONResponse(
            {"error": "Invalid or expired token."},
            status_code=401,
        )
    return user


# ─── Public Endpoints ───────────────────────────────────────────────


@app.post("/api/v1/auth/login")
async def login(request: Request):
    """
    Authenticate and receive a JWT token.
    Send JSON body: {"username": "...", "password": "..."}
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    username = body.get("username", "")
    password = body.get("password", "")

    if not username or not password:
        return JSONResponse(
            {"error": "Missing username or password"},
            status_code=400,
        )

    conn = get_db()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = conn.execute(
        "SELECT * FROM researchers WHERE username = ? AND password_hash = ?",
        (username, password_hash),
    ).fetchone()
    conn.close()

    if not user:
        return JSONResponse(
            {"error": "Invalid credentials. Access denied."},
            status_code=401,
        )

    token = create_token(dict(user))

    return {
        "message": "Authentication successful",
        "token": token,
        "token_type": "Bearer",
        "user": {
            "username": user["username"],
            "name": user["full_name"],
            "role": user["role"],
            "clearance_level": user["clearance_level"],
        },
    }


@app.get("/api/v1/auth/profile")
async def profile(request: Request):
    """View your decoded JWT claims. Useful for debugging."""
    user = require_auth(request)
    if isinstance(user, JSONResponse):
        return user

    return {
        "profile": user,
    }


# ─── Temporal Endpoints ─────────────────────────────────────────────


@app.get("/api/v1/temporal/missions")
async def list_missions(request: Request):
    """
    List temporal missions. Classified missions require clearance level 5.
    """
    user = require_auth(request)
    if isinstance(user, JSONResponse):
        return user

    clearance = user.get("clearance", 0)

    conn = get_db()
    missions = conn.execute("SELECT * FROM missions").fetchall()
    conn.close()

    result = []
    for m in missions:
        mission_data = {
            "id": m["id"],
            "codename": m["codename"],
            "destination_year": m["destination_year"],
            "status": m["status"],
            "clearance_required": m["clearance_required"],
        }

        if m["clearance_required"] <= clearance:
            mission_data["briefing"] = m["briefing"]
        else:
            mission_data["briefing"] = "[REDACTED - INSUFFICIENT CLEARANCE]"

        result.append(mission_data)

    return {
        "missions": result,
        "your_clearance": clearance,
        "total": len(result),
    }


@app.get("/api/v1/temporal/missions/{mission_id}")
async def get_mission(request: Request, mission_id: int):
    """Get detailed mission briefing. Requires sufficient clearance."""
    user = require_auth(request)
    if isinstance(user, JSONResponse):
        return user

    clearance = user.get("clearance", 0)

    conn = get_db()
    mission = conn.execute(
        "SELECT * FROM missions WHERE id = ?", (mission_id,)
    ).fetchone()
    conn.close()

    if not mission:
        return JSONResponse({"error": "Mission not found"}, status_code=404)

    if mission["clearance_required"] > clearance:
        return JSONResponse(
            {
                "error": "ACCESS DENIED - Insufficient clearance",
                "required_clearance": mission["clearance_required"],
                "your_clearance": clearance,
                "message": "Contact Temporal Command for clearance upgrade.",
            },
            status_code=403,
        )

    return {
        "mission": {
            "id": mission["id"],
            "codename": mission["codename"],
            "destination_year": mission["destination_year"],
            "status": mission["status"],
            "clearance_required": mission["clearance_required"],
            "briefing": mission["briefing"],
        }
    }


@app.get("/api/v1/temporal/classified")
async def classified(request: Request):
    user = require_auth(request)
    if isinstance(user, JSONResponse):
        return user

    if user.get("role") != "admin":
        return JSONResponse(
            {
                "error": "ACCESS DENIED - Admin role required",
                "your_role": user.get("role"),
                "required_role": "admin",
            },
            status_code=403,
        )

    return {
        "classification": "TOP SECRET - TEMPORAL COMMAND EYES ONLY",
        "project": "OMEGA PROTOCOL",
        "authorization_code": FLAG,
        "message": "Congratulations, temporal operative. You have breached the highest clearance level.",
        "briefing": (
            "The Omega Protocol contains the coordinates for the origin event - "
            "the point in spacetime where temporal travel was first achieved. "
            "Guard this information with your existence."
        ),
    }


# ─── Debug / Information Disclosure ─────────────────────────────────


@app.get("/api/v1/debug/health")
async def health_check():
    """Public health check - leaks useful info."""
    return {
        "status": "healthy",
        "uptime": "operational",
        "version": "3.7.1",
        "python_jwt_version": jwt.__version__,
        "algorithm": "HS256",
    }


@app.get("/api/v1/debug/token-info")
async def token_info(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(
            {"error": "Send a Bearer token to inspect it."},
            status_code=400,
        )

    token = auth[7:]
    try:
        # Decode WITHOUT verification - shows structure
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        return {
            "header": header,
            "payload": payload,
        }
    except Exception as e:
        return JSONResponse({"error": f"Could not decode token: {e}"}, status_code=400)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
