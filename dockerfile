# Use a lightweight Python image
FROM python:3.11-slim

# Workdir inside the container
WORKDIR /app

# Install dependencies first (faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY . .

# Default command (adjust if you use something else)
# Example: Dash/Flask on port 8000
ENV PORT=8000
EXPOSE 8000

CMD ["python", "app.py"]
