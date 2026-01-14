"""
This module creates a separate ASGI app for serving Prometheus metrics.

When PROMETHEUS_MULTIPROC_DIR is set, this app will automatically find
and aggregate the metrics from all worker processes.
"""
from prometheus_client import make_asgi_app

# Create the ASGI app
metrics_app = make_asgi_app()