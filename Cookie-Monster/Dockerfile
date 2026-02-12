FROM python:3.11-slim

COPY src/app.py /app/app.py
COPY src/flag.txt /flag.txt

RUN pip install --no-cache-dir flask

EXPOSE 8080

CMD ["python", "/app/app.py"]
