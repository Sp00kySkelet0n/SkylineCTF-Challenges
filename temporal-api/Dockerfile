FROM python:3.12-slim

WORKDIR /challenge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV FLAG="HIT{jwt_n0n3_4lg0_t1m3_tr4v3l_cl34r4nc3}"
ENV JWT_SECRET="time"

WORKDIR /challenge/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
