FROM python:3.12-slim

WORKDIR /challenge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV FLAG="HIT{1d0r_4nd_sql1_t1m3_h31st}"
ENV SECRET_KEY="chronobank_secret_key_2147"

WORKDIR /challenge/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
