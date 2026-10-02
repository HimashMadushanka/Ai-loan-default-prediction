FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (build-essential, libgomp1 for XGBoost, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY . .

# Expose ports: 8000 for FastAPI Backend, 8501 for Streamlit Dashboard
EXPOSE 8000
EXPOSE 8501

# Run both FastAPI and Streamlit concurrently
CMD ["sh", "-c", "python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 & streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0"]
