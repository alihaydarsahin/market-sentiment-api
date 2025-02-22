from flask import request, Response
from prometheus_client import Counter, Histogram, Info
import time
from functools import wraps

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')
model_predictions = Counter('model_predictions_total', 'Total model predictions')
model_info = Info('model_version', 'ML model information')

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
        from prometheus_client import generate_latest
        return Response(generate_latest(), mimetype='text/plain') 