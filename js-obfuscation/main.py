"""
CTF Challenge - JS Obfuscation
Difficulty: Easy
Category: Reverse / Obfuscation

Deobfuscate the JavaScript to find the flag.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

app = FastAPI(title="JS Obfuscation", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FLAG = os.environ.get("FLAG", "HIT{0bfusc4t10n_1s_3z}")


def encode_flag_for_js(flag: str) -> list:
    """Encode flag as hex escape sequences for obfuscated JS."""
    parts = []
    chunk_size = 4
    for i in range(0, len(flag), chunk_size):
        chunk = flag[i : i + chunk_size]
        hex_str = "".join(f"\\x{ord(c):02x}" for c in chunk)
        parts.append(hex_str)
    return parts


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    encoded = encode_flag_for_js(FLAG)
    return templates.TemplateResponse(
        "index.html", {"request": request, "flag_parts": encoded}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
