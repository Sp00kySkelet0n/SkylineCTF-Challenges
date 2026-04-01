"""
CTF Challenge - Cookie Admin
Difficulty: Trivial
Vulnerability: Cookie manipulation (role=admin)

Access /admin with cookie role=admin to get the flag.
"""

from fastapi import FastAPI, Request, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn
import os

app = FastAPI(title="Cookie Admin", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FLAG = os.environ.get("FLAG", "HIT{c00k13_r0l3_4dm1n_1s_3z}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    resp = templates.TemplateResponse("index.html", {"request": request})
    if "role" not in request.cookies:
        resp.set_cookie(key="role", value="guess")
    return resp


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request, role: Optional[str] = Cookie(None)):
    if role == "admin":
        return templates.TemplateResponse("admin.html", {"request": request, "flag": FLAG})
    return HTMLResponse("<h1>Access denied</h1><p>Retour <a href='/'>accueil</a></p>", status_code=403)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
