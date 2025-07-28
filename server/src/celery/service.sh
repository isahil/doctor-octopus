#!/bin/bash

# Default values
ACTION="start"
LOG_DIR="./logs"
CELERY_BIN="celery"
CONCURRENCY=5

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --action=*)
            ACTION="${1#*=}"
            ;;
        --log-dir=*)
            LOG_DIR="${1#*=}"
            ;;
        --concurrency=*)
            CONCURRENCY="${1#*=}"
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Create log directory
mkdir -p "$LOG_DIR"

# Function to start celery workers
start_celery() {
    echo "[$(date)] Starting Celery workers and Flower..."
    
    # Start main server worker
    $CELERY_BIN -A src.celery.app worker \
        --hostname=main_server@%h \
        --concurrency=$CONCURRENCY \
        --queues=main_server,celery \
        --loglevel=info \
        --logfile="$LOG_DIR/main_server.log" \
        --pidfile="$LOG_DIR/main_server.pid" \
        --detach

    # # Start notification and monitoring worker
    # $CELERY_BIN -A src.celery.app worker \
    #     --hostname=service@%h \
    #     --concurrency=$CONCURRENCY \
    #     --queues=notification,monitoring \
    #     --loglevel=info \
    #     --logfile="$LOG_DIR/util_server.log" \
    #     --pidfile="$LOG_DIR/util_server.pid" \
    #     --detach
    
    # Start celery beat for periodic tasks
    $CELERY_BIN -A src.celery.app beat \
        --loglevel=info \
        --logfile="$LOG_DIR/beat.log" \
        --pidfile="$LOG_DIR/beat.pid" \
        --detach

    # Start Flower monitoring tool
    $CELERY_BIN -A src.celery.app flower \
        --port=5555 \
        --address=0.0.0.0 \
        --log-file-path="$LOG_DIR/flower.log" \
        --persistent=True \
        --db="$LOG_DIR/flower.db" \
        --pidfile="$LOG_DIR/flower.pid" \
        --detach

    echo "[$(date)] Celery workers and Flower started"
    echo "Flower dashboard: http://localhost:5555"
}

# Function to stop celery workers
stop_celery() {
    echo "[$(date)] Stopping Celery workers and Flower..."

    # Check for PID files and stop processes
    for pid_file in "$LOG_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            echo "[$(date)] Stopping $service_name..."
            
            PID=$(cat "$pid_file")
            if ps -p "$PID" > /dev/null; then
                kill "$PID"
                echo "[$(date)] Process $service_name with PID $PID stopped"
            else
                echo "[$(date)] Process $service_name with PID $PID not running"
            fi
            
            rm -f "$pid_file"
        fi
    done
    
    # Use pkill as backup to make sure all processes are stopped
    pkill -f 'celery worker' || true
    pkill -f 'celery beat' || true
    pkill -f 'celery flower' || true

    echo "[$(date)] All Celery processes stopped"
}

# Function to check status
check_status() {
    echo "[$(date)] Checking Celery workers status..."
    
    for pid_file in "$LOG_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            PID=$(cat "$pid_file")
            
            if ps -p "$PID" > /dev/null; then
                echo "[$(date)] $service_name is running with PID $PID"
            else
                echo "[$(date)] $service_name is not running (stale PID file)"
            fi
        fi
    done
}

# Execute requested action
case "$ACTION" in
    start)
        start_celery
        ;;
    stop)
        stop_celery
        ;;
    restart)
        stop_celery
        sleep 2
        start_celery
        ;;
    status)
        check_status
        ;;
    *)
        echo "Unknown action: $ACTION"
        echo "Usage: $0 --action=[start|stop|restart|status] [--log-dir=DIR] [--concurrency=N]"
        exit 1
        ;;
esac

exit 0
