import multiprocessing
import os

# Server socket
bind = '0.0.0.0:' + os.environ.get('PORT', '8000')

# Worker processes
# For ML apps, memory can be a bottleneck, so keep workers conservative
workers = 2
worker_class = 'gthread'
threads = 4

# Timeout for ML Prediction (can take a few seconds on CPU)
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
