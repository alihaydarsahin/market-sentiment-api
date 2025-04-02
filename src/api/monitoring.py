from flask import request, Response
from prometheus_client import Counter, Histogram, Info, Gauge
import time
from functools import wraps
import psutil
import os

# Basic HTTP Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Model Metrics
model_predictions = Counter('model_predictions_total', 'Total model predictions')
model_prediction_latency = Histogram('model_prediction_duration_seconds', 'Model inference latency')
model_info = Info('model_version', 'ML model information')

# System Metrics
system_memory = Gauge('system_memory_usage_bytes', 'System memory usage')
system_cpu = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')

# Input Validation Metrics
validation_errors = Counter('input_validation_errors_total', 'Input validation errors', ['type'])

def track_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        method = request.method
        endpoint = request.endpoint
        
        # Increment request counter
        request_count.labels(method=method, endpoint=endpoint).inc()
        
        # Track request duration
        start_time = time.time()
        response = f(*args, **kwargs)
        duration = time.time() - start_time
        request_latency.observe(duration)
        
        return response
    return decorated_function

def track_prediction(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            model_prediction_latency.observe(duration)
            model_predictions.inc()
            return result
        except ValueError as e:
            validation_errors.labels(type=str(e)).inc()
            raise
    return decorated_function

def update_system_metrics():
    """Update system resource metrics"""
    process = psutil.Process(os.getpid())
    system_memory.set(process.memory_info().rss)
    system_cpu.set(process.cpu_percent())

def init_monitoring(app):
    # Set model info
    model_info.info({
        'version': '1.0.0',
        'type': 'RandomForest',
        'last_trained': '2025-02-20'
    })
    
    # Add prometheus metrics endpoint
    @app.route('/metrics')
    def metrics():
        update_system_metrics()  # Update system metrics before serving
        from prometheus_client import generate_latest
        return Response(generate_latest(), mimetype='text/plain') 