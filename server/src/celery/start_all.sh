#!/bin/bash

echo "[$(date)] Starting Doctor Octopus system..."

export NODE_ENV=${NODE_ENV:-dev}
export PYTHONPATH=$(pwd)

# Start Celery workers and Flower
echo "[$(date)] Starting Celery workers..."
sh src/celery/service.sh --action=start

# Wait for workers to initialize
echo "[$(date)] Waiting for workers to initialize..."
sleep 5

# Launch all services
echo "[$(date)] Launching application services..."
python src/celery/launcher.py --services all

echo "[$(date)] System startup complete!"
echo "Open http://localhost:5555 to monitor the system with Flower"
echo "To stop all services, run: ./stop_all.sh"


# Example usage:
# Start specific services
# python launcher.py --services main util
# Stop specific services
# python stop_servers.py --service main_server --port 8000
# Manage Celery workers
# ./service.sh --action=status
# ./service.sh --action=restart