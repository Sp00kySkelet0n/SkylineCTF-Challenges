"""
CTF Challenge - JS Obfuscation 3
Difficulty: Hard
Category: Reverse / Obfuscation

Misdirection: homepage fake challenge decodes to path hint.
Real flag on hidden page /0x7a2f
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import base64
import random

app = FastAPI(title="JS Obfuscation 3", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

FLAG = os.environ.get("FLAG", "HIT{0bfusc4t10n_v3_tr0ll3d}")
FAKE_MESSAGE = "0x7a2f"

# Custom base64 alphabet - not standard, breaks atob/btoa
CUSTOM_ALPHABET = "s3HXunU82JdSpkQWzqeTfLZox/hY4E6VyKA9cta1Mjwmg7N0BCblFi5rG+I=PRvDO"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


def custom_b64encode(data: str) -> str:
    raw = base64.b64encode(data.encode()).decode()
    return "".join(CUSTOM_ALPHABET[STANDARD_ALPHABET.index(c)] for c in raw)


def encode_fake_payload() -> str:
    """Custom base64 + XOR with position-dependent key."""
    msg = FAKE_MESSAGE
    key = 0x3F
    xored = bytes((ord(c) ^ (key + i) % 256) for i, c in enumerate(msg))
    b64 = base64.b64encode(xored).decode()
    return "".join(CUSTOM_ALPHABET[STANDARD_ALPHABET.index(c)] for c in b64)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    fake_payload = encode_fake_payload()
    return templates.TemplateResponse(
        "index.html", {"request": request, "fake_payload": fake_payload}
    )


def random_button_position():
    top = random.randint(5, 85)
    left = random.randint(5, 85)
    return {"top": top, "left": left}


@app.get("/0x7a2f")
async def step_start(request: Request):
    pos = random_button_position()
    return templates.TemplateResponse(
        "step.html",
        {"request": request, "step": 0, "next_url": "/0x7a2f/1", "pos": pos},
    )


@app.get("/0x7a2f/{step:int}")
async def redirect_chain(request: Request, step: int):
    if step < 20:
        pos = random_button_position()
        return templates.TemplateResponse(
            "step.html",
            {
                "request": request,
                "step": step,
                "next_url": f"/0x7a2f/{step + 1}",
                "pos": pos,
            },
        )
    return templates.TemplateResponse(
        "fake404.html", {"request": request, "flag": FLAG}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
