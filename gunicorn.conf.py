# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:" + str(os.getenv('PORT', 8000))
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, this can help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# Process naming
proc_name = 'codeinterviewpro'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Application
wsgi_module = 'core.wsgi:application'
pythonpath = '/app'

# Worker timeout
graceful_timeout = 30

# Preload application
preload_app = True