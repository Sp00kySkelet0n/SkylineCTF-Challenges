FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libexpat1 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY src/main.py ./main.py
COPY src/bot.py ./bot.py
COPY src/start.sh ./start.sh
COPY src/static ./static
COPY src/templates ./templates
COPY src/flag.txt /flag.txt

ENV FLAG_FILE=/flag.txt
ENV ADMIN_SECRET="s3cr3t_4dm1n_t0k3n_d0_n0t_l34k"
ENV APP_URL="http://localhost:8000"
ENV BOT_URL="http://localhost:8000"

EXPOSE 8000 3000

RUN chmod +x start.sh
CMD ["./start.sh"]
