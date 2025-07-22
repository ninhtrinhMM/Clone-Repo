import time
import logging
import joblib
import numpy as np
from typing import List
from functools import wraps
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

# Import OpenTelemetryy
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

# Import OpenTelemetry Metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import get_meter_provider, set_meter_provider

# Import Prometheus client
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
# Bổ sung 
from contextlib import asynccontextmanager 

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resource chung cho cả tracing và metrics
resource = Resource.create({SERVICE_NAME: "ml-prediction-service"})

# 1. Thiết lập Tracing với Jaeger
set_tracer_provider(
    TracerProvider(resource=resource)
)

# Tạo Jaeger Exporterttt
jaeger_exporter = JaegerExporter(
    #agent_host_name="jaeger",
    agent_host_name="jaeger.default.svc.cluster.local",  # Sử dụng DNS của Jaeger trong Kubernetes
    agent_port=6831,
)

# Thêm processor để gửi span đến Jaeger
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Lấy tracer
tracer = get_tracer_provider().get_tracer("ml-prediction", "0.1.2")


# 2. Tạo Prometheus metrics trực tiếp bằng prometheus_client
model_request_counter = Counter(
    'model_request_total',
    'Total number of requests sent to model',
    ['endpoint']
)

prediction_duration_histogram = Histogram(
    'ml_prediction_duration_seconds',
    'Time spent on predictions',
    ['endpoint', 'status']
)

error_counter = Counter(
    'ml_errors_total',
    'Total number of errors',
    ['operation', 'error_type']
)

### Bổ sung Lifespan context
cached_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Service start...")
    global cached_model
    try:
        cached_model = load_model()
        logger.info("Model load succesfully")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")
    
    yield
    
    # Shutdown n cleanup
    logger.info("Shutting down ML Prediction Service...")
    cached_model = None
    
# Tạo FastAPI app
app = FastAPI(title="ML Prediction Service", 
              version="0.1.0",
              lifespan=lifespan)

# 2. Tạo decorator trace-span để tự động trace cho các function
def trace_span(span_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

# 3. Load model với tracing
@trace_span("model-loader")
def load_model():
    try:
        model = joblib.load("model_ml.joblib")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        
        # Thiết lập metrics error_counter khi load model
        
        error_counter.labels(operation="model_load", error_type=type(e).__name__).inc()
        
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

# 4. Tracing cho hàm dự đoán predictor
@trace_span("predictor")
def make_prediction(model, features):
    start_time = time.time()
    
    try:
        logger.info(f"Making prediction with features: {features}")
        
        # Kiểm tra input
        if not features:
            raise ValueError("Features cannot be empty")
        
        # Chuyển đổi features thành numpy array
        features_array = np.array([features])
        
        # Thực hiện dự đoán
        prediction = model.predict(features_array)
        
        logger.info(f"Prediction result: {prediction}")
        
        # Chuyển đổi kết quả thành list
        result = prediction.tolist()
        
        # Thiết lập metric cho prediction_duration_histogram
        
        duration = time.time() - start_time
        prediction_duration_histogram.labels(endpoint="internal", status="success").observe(duration)
        
        return result
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        
        # Thiết lập metric cho error_counter
        
        duration = time.time() - start_time
        prediction_duration_histogram.labels(endpoint="internal", status="error").observe(duration)
        error_counter.labels(operation="prediction", error_type=type(e).__name__).inc()
        
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# 5. API endpoint với tracing và metrics
@app.post("/predict")
def predict(features: List[float]):
    endpoint_start_time = time.time()
    
    # Đếm số lượng request được gửi đến model
    model_request_counter.labels(endpoint="/predict").inc()
    
    try:
        with tracer.start_as_current_span("prediction-endpoint") as span:
            logger.info(f"Received prediction request with features: {features}")
            
            # Thêm thông tin vào span
            span.set_attribute("input.features", str(features))
            span.set_attribute("input.length", len(features))
            
            # Load model
            model = load_model()
            
            # Thực hiện dự đoán
            prediction = make_prediction(model, features)
            
            # Thêm thông tin prediction vào span
            span.set_attribute("prediction.result", str(prediction))
            span.set_attribute("prediction.success", True)
            
            # Record endpoint metrics
            endpoint_duration = time.time() - endpoint_start_time
            prediction_duration_histogram.labels(endpoint="/predict", status="success").observe(endpoint_duration)
            
            logger.info(f"Returning prediction: {prediction}")
            return {"prediction": prediction, "status": "success"}
            
    except HTTPException as he:
        # Record HTTP error metrics
        endpoint_duration = time.time() - endpoint_start_time
        prediction_duration_histogram.labels(endpoint="/predict", status="http_error").observe(endpoint_duration)
        error_counter.labels(operation="endpoint", error_type="HTTPException").inc()
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in prediction endpoint: {e}")
        
        # Record unexpected error metrics
        endpoint_duration = time.time() - endpoint_start_time
        prediction_duration_histogram.labels(endpoint="/predict", status="error").observe(endpoint_duration)
        error_counter.labels(operation="endpoint", error_type=type(e).__name__).inc()
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

### Endpoint để expose Prometheus metrics ###
@app.get("/metrics")
def get_metrics():
    """Endpoint để Prometheus scrape metrics"""
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

# Health check endpoints
@app.get("/")
def root():
    return {"message": "ML Prediction Service is running"}

@app.get("/health")
def health():
    try:
        # Kiểm tra xem có thể load model được không
        try:
            load_model()
            model_loaded = True
        except:
            model_loaded = False
        
        return {
            "status": "healthy",
            "model_loaded": model_loaded,
            "service": "ml-prediction-service",
            "metrics_endpoint": "/metrics"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Prediction Service...")
    uvicorn.run(app, host="0.0.0.0", port=5000)