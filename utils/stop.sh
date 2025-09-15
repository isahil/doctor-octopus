#!/bin/bash

echo "[$(date)] Stopping Doctor Octopus services..."

# Function to safely stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    local log_file="logs/${service_name}.log"
    
    if [ ! -f "$pid_file" ]; then
        echo "[$(date)] No PID file found for $service_name"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    
    # Validate PID
    if [ -z "$pid" ] || ! [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "[$(date)] Invalid PID in $pid_file: '$pid'"
        rm -f "$pid_file"
        return 1
    fi
    
    # Check if process exists
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "[$(date)] Process $pid for $service_name is not running (stale PID)"
        rm -f "$pid_file"
        return 0
    fi
    
    # Verify this is actually our process
    local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
    if ! [[ "$cmd" =~ (npm|node|python|uvicorn) ]]; then
        echo "[$(date)] WARNING: PID $pid is not a Node.js/Python process (cmd: $cmd)"
        echo "[$(date)] Skipping kill to avoid stopping wrong process"
        rm -f "$pid_file"
        return 1
    fi
    
    echo "[$(date)] Stopping $service_name (PID: $pid, CMD: $cmd)..."
    echo "[$(date)] Stopping $service_name..." >> "$log_file"
    
    # Try graceful shutdown first
    kill -TERM "$pid" 2>/dev/null
    
    # Wait up to 15 seconds for graceful shutdown
    local count=0
    while [ $count -lt 15 ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] $service_name stopped gracefully"
            echo "[$(date)] $service_name stopped gracefully" >> "$log_file"
            rm -f "$pid_file"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill if still running
    echo "[$(date)] Force killing $service_name (PID: $pid)..."
    echo "[$(date)] Force killing $service_name" >> "$log_file"
    kill -9 "$pid" 2>/dev/null
    
    # Wait a moment and verify
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        echo "[$(date)] ERROR: Failed to stop $service_name (PID: $pid)"
        return 1
    else
        echo "[$(date)] $service_name force killed successfully"
        echo "[$(date)] $service_name force killed" >> "$log_file"
        rm -f "$pid_file"
        return 0
    fi
}

# Stop all services
services=("notification" "server" "client")  # Stop in reverse order
stopped_count=0
failed_count=0

for service in "${services[@]}"; do
    if stop_service "$service"; then
        stopped_count=$((stopped_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
done

echo "[$(date)] Stop operation completed: $stopped_count stopped, $failed_count failed"

# Clean up any remaining stale PID files
echo "[$(date)] Cleaning up stale PID files..."
for pid_file in logs/*.pid; do
    if [ -f "$pid_file" ]; then
        service_name=$(basename "$pid_file" .pid)
        pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] Removing stale PID file: $pid_file"
            rm -f "$pid_file"
        fi
    fi
done

# Show final status
echo "[$(date)] Final process check:"
for service in client server notification; do
    if [ -f "logs/${service}.pid" ]; then
        pid=$(cat "logs/${service}.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo "  ✗ $service still running (PID: $pid)"
        else
            echo "  ✓ $service stopped"
        fi
    else
        echo "  ✓ $service stopped (no PID file)"
    fi
done

echo "[$(date)] Doctor Octopus services stopped"
