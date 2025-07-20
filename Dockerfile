FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements 
COPY requirements.txt .

# Cài đặt Dependency
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code

COPY ML-app.py .

COPY jupyter-notebook-model/model_ml.joblib /app/
# Copy model_ml.joblib file vào COntainer

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "ML-app.py"]