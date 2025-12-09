# Gunicorn configuration file for production deployment
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout
# Increased to 120 seconds for ML classification requests that may take longer
timeout = 120
keepalive = 5

# Logging
accesslog = "./log/gunicorn_access.log"
errorlog = "./log/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "controle_financeiro_api"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in future)
# keyfile = None
# certfile = None

