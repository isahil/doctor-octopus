#!/bin/bash

SERVICE=$1
DEBUG=${2:-false}

source ./utils/env-loader.sh

if [ -z "$SERVICE" ]; then
    echo "Usage: $0 <service> [debug]"
    echo "Services: client, server, notification, all"
    exit 1
fi

restart_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    local log_file="logs/${service_name}.log"
    
    echo "[$(date)] Restarting $service_name..."
    
    # Stop the service first
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] Stopping existing $service_name (PID: $pid)..."
            kill "$pid"
            sleep 3
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "[$(date)] Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null
                sleep 1
            fi
        fi
        rm -f "$pid_file"
    fi

    echo "[$(date)] Starting $service_name..."
    case "$service_name" in
        "client")
            nohup npm run client >> "$log_file" 2>&1 &
            ;;
        "server")
            nohup npm run server >> "$log_file" 2>&1 &
            ;;
        "notification")
            nohup npm run notification >> "$log_file" 2>&1 &
            ;;
        *)
            echo "[$(date)] Unknown service: $service_name"
            return 1
            ;;
    esac
    
    local new_pid=$!
    sleep 3
    
    if kill -0 "$new_pid" 2>/dev/null; then
        echo "$new_pid" > "$pid_file"
        echo "[$(date)] $service_name restarted with PID: $new_pid"
        echo "[$(date)] $service_name restarted with PID: $new_pid" >> "$log_file"
        return 0
    else
        echo "[$(date)] Failed to restart $service_name"
        return 1
    fi
}

# Restart services
case "$SERVICE" in
    "all")
        ./utils/stop.sh
        sleep 2
        ./utils/start.sh "$DEBUG"
        ;;
    "client"|"server"|"fixme"|"notification")
        restart_service "$SERVICE"
        ;;
    *)
        echo "Unknown service: $SERVICE"
        echo "Available services: client, server, fixme, notification, all"
        exit 1
        ;;
esac