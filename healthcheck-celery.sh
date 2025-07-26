#!/bin/sh
# Robust Celery healthcheck: returns 0 if at least one worker responds, 1 otherwise
celery -A erp_system inspect ping -d celery@$(hostname) | grep -q 'pong' && exit 0 || exit 1
