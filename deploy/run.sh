#!/bin/bash
set -euo pipefail
set -a
source /Users/mac/djangovueblog-data/env
set +a
exec /Users/mac/djangovueblog-runtime/venv/bin/gunicorn \
  --bind 127.0.0.1:8899 \
  --workers 3 \
  --timeout 60 \
  --access-logfile /Users/mac/djangovueblog-data/logs/access.log \
  --error-logfile /Users/mac/djangovueblog-data/logs/error.log \
  config.wsgi:application
