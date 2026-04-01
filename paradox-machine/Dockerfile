FROM python:3.12-slim

WORKDIR /challenge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

ENV FLAG="HIT{sst1_p4r4d0x_rce_t1m3l1n3_br34ch}"

# Write flag to /flag.txt at container start
RUN echo "HIT{sst1_p4r4d0x_rce_t1m3l1n3_br34ch}" > /flag.txt

WORKDIR /challenge/app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
