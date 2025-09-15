#!/bin/bash

DEBUG=$1

source ./utils/env-loader.sh

# PID management functions below
cleanup_stale_pids() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [ -n "$pid" ] && [ "$pid" -gt 0 ] 2>/dev/null; then

            echo "[$(date)] Checking existing PID $pid for $service_name"
            if kill -0 "$pid" 2>/dev/null; then
                local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "")
                echo "[$(date)] CMD = $cmd"
                if [[ "$cmd" =~ (npm|node|python|uvicorn) ]]; then
                    echo "[$(date)] Found running $service_name process with PID: $pid"
                    return 0  # PID is valid and running
                else
                    echo "[$(date)] PID $pid exists but is not a $service_name process (cmd: $cmd)"
                fi
            else
                echo "[$(date)] Stale PID $pid found for $service_name, cleaning up"
            fi
        fi

        rm -f "$pid_file" # Remove stale PID file
    fi
    return 1  # No valid PID found
}

# Function to save PID after validation
save_pid_with_validation() {
    local initial_pid=$1
    local service_name=$2
    local pid_file="logs/${service_name}.pid"
    local log_file="logs/${service_name}.log"
    echo "[$(date)] $service_name's initial process PID: $initial_pid"
    echo $initial_pid > "$pid_file"

    sleep 5 # Wait a moment to ensure process starts properly

    pid=$(cat $pid_file)
    while read -r pid || [[ -n "$pid" ]]; do
        echo "[$(date)] The $service_name's process PID logged: [$pid]"
        if kill -0 "$pid" 2>/dev/null; then
            echo "[$(date)] The $service_name started successfully with PID: [$pid]" >> "$log_file"
            return 0
        else
            echo "[$(date)] ERROR: The $service_name process $pid failed to start properly"
            rm -f "$pid_file"
            return 1
        fi
    done < "$pid_file"
}

get_service_pid() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    else
        echo ""
    fi
}

echo "[$(date)] Starting background processes for Doctor Octopus app..."
echo "[$(date)] Checking for existing processes and clean up stale PIDs..."
for process in client server notification; do
    cleanup_stale_pids "logs/${process}.pid" "$process" && {
        echo "[$(date)] $process is already running. Stop it first with: npm run stop"
        exit 1
    }
done

echo "[$(date)] Starting the client server..."
nohup npm run client >> logs/client.log 2>&1 &
CLIENT_PID=$!
if save_pid_with_validation "$CLIENT_PID" "client"; then
    echo "[$(date)] The client service process started. [$CLIENT_PID]"
else
    echo "[$(date)] Failed to start client service"
    exit 1
fi

echo "[$(date)] Starting the main server..."
nohup npm run server >> logs/server.log 2>&1 &
SERVER_PID=$!
if save_pid_with_validation "$SERVER_PID" "server"; then
    echo "[$(date)] The main server's parent process started. [$SERVER_PID]"
    server_pids=$(lsof -ti:8000)
    echo "[$(date)] Main server actual process PID(s) on port 8000: $server_pids"
else
    echo "[$(date)] Failed to start server service"
    client_pid=$(get_service_pid "client")
    [ -n "$client_pid" ] && kill "$client_pid" 2>/dev/null
    rm -f logs/client.pid
    exit 1
fi

echo "[$(date)] Starting the notification server..."
nohup npm run notification >> logs/notification.log 2>&1 &
NOTIFICATION_PID=$!
if save_pid_with_validation "$NOTIFICATION_PID" "notification"; then
    echo "[$(date)] Notification service process started. [$NOTIFICATION_PID]"
else
    echo "[$(date)] Failed to start notification service"
    client_pid=$(get_service_pid "client")
    server_pid=$(get_service_pid "server")
    [ -n "$client_pid" ] && kill "$client_pid" 2>/dev/null
    [ -n "$server_pid" ] && kill "$server_pid" 2>/dev/null
    # rm -f logs/client.pid logs/server.pid
    # exit 1
fi

echo "[$(date)] === Port Status ==="
lsof -i :3000 >/dev/null 2>&1 && echo "✓ Port 3000 (Client) is listening" || echo "✗ Port 3000 not listening"
lsof -i :8000 >/dev/null 2>&1 && echo "✓ Port 8000 (Server) is listening" || echo "✗ Port 8000 not listening"
lsof -i :8001 >/dev/null 2>&1 && echo "✓ Port 8001 (Fixme) is listening" || echo "✗ Port 8001 not listening"

echo "[$(date)] All background processes started!"

if [ "$DEBUG" = "true" ]; then
    echo "[$(date)] Debug mode is ON"
    echo "[$(date)] Waiting for services to initialize..."
    sleep 7

    echo "[$(date)] === Recent Logs ==="
    for service in client server notification; do
        echo "[$(date)] --- ${service^} Log ---"
        if [ -f "logs/${service}.log" ]; then
            tail -5 "logs/${service}.log" | sed 's/^/  /'
        else
            echo "[$(date)] No log file found"
        fi
    done

    # Set up signal handlers for graceful shutdown
    cleanup_on_exit() {
        echo "[$(date)] Received shutdown signal, stopping services..."
        
        # Read PIDs and validate before killing
        for service in client server notification; do
            pid_file="logs/${service}.pid"
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file")
                if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                    echo "[$(date)] Stopping $service (PID: $pid)..."
                    kill "$pid"
                    
                    # Wait for graceful shutdown
                    for i in {1..10}; do
                        if ! kill -0 "$pid" 2>/dev/null; then
                            echo "[$(date)] $service stopped gracefully"
                            break
                        fi
                        sleep 1
                    done
                    
                    # Force kill if still running
                    if kill -0 "$pid" 2>/dev/null; then
                        echo "[$(date)] Force killing $service (PID: $pid)..."
                        kill -9 "$pid" 2>/dev/null
                    fi
                fi
                rm -f "$pid_file"
            fi
        done
        
        exit 0
    }

    trap cleanup_on_exit SIGTERM SIGINT

    # Keep container running and monitor processes (FOREGROUND for Docker)
    monitor_processes() {
        echo "[$(date)] Started process monitoring (Docker mode)..."
        while true; do
            # Check if all services are still running
            services_running=0
            
            for service in client server notification; do
                pid_file="logs/${service}.pid"
                if [ -f "$pid_file" ]; then
                    pid=$(cat $pid_file)
                    if kill -0 "$pid" 2>/dev/null; then
                        services_running=$((services_running + 1))
                    else
                        echo "[$(date)] WARNING: $service (PID: $pid) has stopped unexpectedly"
                        rm -f "$pid_file"
                    fi
                fi
            done
            
            if [ $services_running -eq 0 ]; then
                echo "[$(date)] All services have stopped. Exiting..."
                break
            fi
            
            sleep 10
        done
    }

    # Start monitoring in background
    monitor_processes
else
    echo "[$(date)] Local development mode - Services running in background"
    echo "[$(date)] Services started successfully:"
    echo "  - Client: http://localhost:3000"
    echo "  - Server: http://localhost:8000"
    echo "[$(date)] Use 'npm run stop' to stop services"
    echo "[$(date)] Use 'npm run status' to check service status"

    exit 0
fi