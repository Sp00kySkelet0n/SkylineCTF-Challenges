FROM python:3.12-slim

WORKDIR /challenge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/main.py ./main.py
COPY src/static ./static
COPY src/templates ./templates
COPY src/flag.txt /flag.txt

ENV FLAG_FILE=/flag.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
