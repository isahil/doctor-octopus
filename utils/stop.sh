#!/bin/bash

echo "[$(date)] Stopping Doctor Octopus services..."
services=("notification" "server" "client" "fixme")  # Stops in reverse order

# Function to safely stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    local log_file="logs/${service_name}.log"
    
    if [ ! -f "$pid_file" ]; then
        echo "[$(date)] No PID file found for $service_name"
        return 0
    fi
    
    local pids_str=$(cat "$pid_file")
    
    # Handle multiple PIDs (space-separated)
    local pids=()
    for pid in $pids_str; do
        # Validate each PID
        if [ -z "$pid" ] || ! [[ "$pid" =~ ^[0-9]+$ ]]; then
            echo "[$(date)] Invalid PID in $pid_file: '$pid'"
            continue
        fi
        pids+=("$pid")
    done
    
    # If no valid PIDs found
    if [ ${#pids[@]} -eq 0 ]; then
        echo "[$(date)] No valid PIDs found in $pid_file"
        rm -f "$pid_file"
        return 1
    fi
    
    local all_stopped=true
    
    # Try graceful shutdown for all PIDs
    for pid in "${pids[@]}"; do
        # Check if process exists
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] Process $pid for $service_name is not running (stale PID)"
            continue
        fi
        
        # Verify this is actually our process
        local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
        if ! [[ "$cmd" =~ (npm|node|python|uvicorn) ]]; then
            echo "[$(date)] WARNING: PID $pid is not a Node.js/Python process (cmd: $cmd)"
            echo "[$(date)] Skipping kill to avoid stopping wrong process"
            continue
        fi
        
        echo "[$(date)] Stopping $service_name (PID: $pid, CMD: $cmd)..."
        echo "[$(date)] Stopping $service_name (PID: $pid)..." >> "$log_file"
        
        # Try graceful shutdown
        kill -TERM "$pid" 2>/dev/null
    done
    
    # Wait up to 15 seconds for graceful shutdown of all processes
    local count=0
    while [ $count -lt 15 ]; do
        local running=false
        for pid in "${pids[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                running=true
                break
            fi
        done
        
        if [ "$running" = false ]; then
            echo "[$(date)] $service_name stopped gracefully"
            echo "[$(date)] $service_name stopped gracefully" >> "$log_file"
            rm -f "$pid_file"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Force kill any remaining processes
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] Force killing $service_name (PID: $pid)..."
            echo "[$(date)] Force killing $service_name (PID: $pid)" >> "$log_file"
            kill -9 "$pid" 2>/dev/null
        fi
    done
    
    # Wait a moment and verify all are killed
    sleep 2
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] ERROR: Failed to stop $service_name (PID: $pid)"
            all_stopped=false
        fi
    done
    
    if [ "$all_stopped" = true ]; then
        echo "[$(date)] $service_name force killed successfully"
        echo "[$(date)] $service_name force killed" >> "$log_file"
        rm -f "$pid_file"
        return 0
    else
        echo "[$(date)] ERROR: Failed to stop some processes for $service_name"
        return 1
    fi
}

# Stop all services
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
for service in "${services[@]}"; do
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
