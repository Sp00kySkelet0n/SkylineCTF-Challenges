#!/bin/bash

# Start the admin bot in background
python -m uvicorn bot:bot_app --host 0.0.0.0 --port 3000 &

# Start the main web app
python -m uvicorn main:app --host 0.0.0.0 --port 8000
