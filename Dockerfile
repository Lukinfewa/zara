FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY zara_bot_unico.py .

CMD ["python", "zara_bot_unico.py"]
