"""
CTF Challenge - JS Obfuscation 2
Difficulty: Medium
Category: Reverse / Obfuscation

Multi-layer obfuscation, requires document.currentScript context.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import base64

app = FastAPI(title="JS Obfuscation 2", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FLAG = os.environ.get("FLAG", "HIT{0bfusc4t10n_v2_h4rd3r}")
XOR_KEY = 0x5A


def encode_payload(flag: str) -> str:
    """XOR with key then base64."""
    xored = bytes(c ^ XOR_KEY for c in flag.encode())
    return base64.b64encode(xored).decode()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    payload = encode_payload(FLAG)
    return templates.TemplateResponse(
        "index.html", {"request": request, "payload": payload}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
