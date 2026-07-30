from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette_exporter import PrometheusMiddleware
import time


REQUEST_COUNT = Counter('https_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('https_request_duration_seconds', 'HTTP request Latency', ['method', 'endpoint'])


class CustomPrometheusMiddleware(PrometheusMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        endpoint = request.url.path

        REQUEST_COUNT.labels(request.method, endpoint=endpoint, http_status=response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, endpoint=endpoint).observe(duration)

        return response


def setup_metrics(app):
    app.add_middleware(CustomPrometheusMiddleware)

    @app.get("/Trscvnso_123q_adskk", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)