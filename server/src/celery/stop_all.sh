#!/bin/bash

echo "[$(date)] Stopping Doctor Octopus system..."

# Stop all services
echo "[$(date)] Stopping application services..."
python terminate.py

# Wait for services to stop
echo "[$(date)] Waiting for services to stop..."
sleep 3

# Stop Celery workers and Flower
echo "[$(date)] Stopping Celery workers..."
./service.sh --action=stop

echo "[$(date)] System shutdown complete!"
