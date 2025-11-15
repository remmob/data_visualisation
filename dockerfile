# Basis image
FROM python:3.11-slim

# Werkdirectory
WORKDIR /app

# Dependencies installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopiëren
COPY . .

# Start command
CMD ["python", "app.py"]
