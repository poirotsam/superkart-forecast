# ---------- Stage: runtime ----------
FROM python:3.11-slim
 
WORKDIR /app
 
# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*
 
# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# App files
COPY superkart_backend.py .
COPY superkart_model.joblib .
 
# Expose the API port
EXPOSE 7860
 
# Serve with gunicorn (2 workers is plenty for a Codespaces demo)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--timeout", "120", "superkart_backend:superkart_api"]
