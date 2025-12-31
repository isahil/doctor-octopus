#!/bin/bash

echo "[$(date)] Doctor Octopus Service Status"
echo "======================================"

# Function to check service status
check_service_status() {
    local service_name=$1
    local expected_port=$2
    local pid_file="logs/${service_name}.pid"
    
    printf "%-12s: " "$service_name"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
            local port_status=""
            if [ -n "$expected_port" ]; then
                if lsof -ti:$expected_port >/dev/null 2>&1; then
                    port_status=" (port :$expected_port ✓)"
                else
                    port_status=" (port :$expected_port ✗)"
                fi
            fi
            echo "RUNNING (PID: $pid, CMD: $cmd)$port_status"
            return 0
        else
            echo "STOPPED (stale PID: $pid)"
            return 1
        fi
    else
        echo "STOPPED (no PID file)"
        return 1
    fi
}

# Check each service
check_service_status "client" "3000"
check_service_status "server" "8000"  
check_service_status "fixme" "8001"

echo
echo "Port Usage:"
echo "----------"
for port in 3000 8000 8001; do
    if lsof -ti:$port >/dev/null 2>&1; then
        pid=$(lsof -ti:$port)
        cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        echo "  Port :$port - PID: $pid ($cmd)"
    else
        echo "  Port :$port - Available"
    fi
done

echo
echo "Recent Activity:"
echo "---------------"
for service in client server fixme; do
    log_file="logs/${service}.log"
    if [ -f "$log_file" ]; then
        echo "$service (last 2 lines):"
        tail -2 "$log_file" | sed 's/^/  /'
    fi
done
