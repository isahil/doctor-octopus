#!/bin/bash
SERVICE=$1
if [ -z "$SERVICE" ]; then
    echo "Error: No service specified"
    echo "Usage: npm run [client|server|notification|fixme] [debug]"
    echo "Example: npm run client prod false"
    exit 1
fi

DEBUG=${2:-false} # Run the processes in foreground for Debugging/Docker if second argument is "true"

source ./utils/env-loader.sh

echo "Starting $SERVICE service in $(pwd) with NODE_ENV=$NODE_ENV and DEBUG=$DEBUG"

# Detect if running in Docker
if [ -f /.dockerenv ]; then
    echo "[Docker Mode] Running $SERVICE in foreground (Docker detected)"
    # In Docker, run service directly without backgrounding
    case "$SERVICE" in
        "client")
            cd client && npm run build && npm run serve -- --host 0.0.0.0 --port 3000
            # npm run client:prod
            exit $?
            ;;
        "server")
            cd server && poetry run python3 initialize.py && poetry run uvicorn server:fastapi_app --host 0.0.0.0 --port 8000
            # npm run server
            exit $?
            ;;
        "fixme")
            cd fixme && poetry run uvicorn server:fastapi_app --host 0.0.0.0 --port 8001
            # npm run fixme
            exit $?
            ;;
        "notification")
            cd server && poetry run python3 src/component/notification.py
            # npm run notification
            exit $?
            ;;
        *)
            echo "Unknown service: $SERVICE"
            exit 1
            ;;
    esac
fi

client_script="client"
if [ "$NODE_ENV" = "prod" ]; then
    client_script="client:prod"
fi

# Set services array based on SERVICE parameter
if [ "$SERVICE" = "all" ]; then
    services=("client" "server" "notification" "fixme")
else
    services=("$SERVICE")
fi

client_log_file="logs/client.log"
server_log_file="logs/server.log"
notification_log_file="logs/notification.log"
fixme_log_file="logs/fixme.log"

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

# Function to save PID after validation. TODO: improve validation logic
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
            
            # For services that bind to ports, detect all actual process PIDs
            local port=""
            case "$service_name" in
                "client")
                    port=3000
                    ;;
                "server")
                    port=8000
                    ;;
                "fixme")
                    port=8001
                    ;;
            esac
            
            if [ -n "$port" ]; then
                sleep 2 # Give processes time to bind to port
                local actual_pids=$(lsof -ti:$port 2>/dev/null | sort -u | tr '\n' ' ')
                if [ -n "$actual_pids" ]; then
                    echo "[$(date)] Detected $service_name process PIDs on port $port: $actual_pids"
                    echo "$actual_pids" > "$pid_file"
                    echo "[$(date)] $service_name process PIDs saved to $pid_file" >> "$log_file"
                fi
            fi
            
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

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "client" ]; then
    echo "[$(date)] Starting the client server..."
    nohup npm run "$client_script" >> "$client_log_file" 2>&1 &
    CLIENT_PID=$!
    if save_pid_with_validation "$CLIENT_PID" "client"; then
        echo "[$(date)] The client service process started. [$CLIENT_PID]"
        echo "[$(date)] Client logs at >> $client_log_file"
    else
        echo "[$(date)] Failed to start client service"
        exit 1
    fi
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "server" ]; then
    echo "[$(date)] Starting the main server..."
    nohup npm run server >> "$server_log_file" 2>&1 &
    SERVER_PID=$!
    if save_pid_with_validation "$SERVER_PID" "server"; then
        echo "[$(date)] The main server's parent process started. [$SERVER_PID]"
        server_pids=$(lsof -ti:8000 | tr '\n' ',')
        echo "[$(date)] Main server actual process PID(s) on port 8000: ($server_pids)"
        echo "[$(date)] Server logs at >> $server_log_file"
    else
        echo "[$(date)] Failed to start server service"
        client_pid=$(get_service_pid "client")
        [ -n "$client_pid" ] && kill "$client_pid" 2>/dev/null
        rm -f logs/client.pid
        exit 1
    fi
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "notification" ]; then
    echo "[$(date)] Starting the notification server..."
    nohup npm run notification >> "$notification_log_file" 2>&1 &
    NOTIFICATION_PID=$!
    if save_pid_with_validation "$NOTIFICATION_PID" "notification"; then
        echo "[$(date)] Notification service process started. [$NOTIFICATION_PID]"
        echo "[$(date)] Notification logs at >> $notification_log_file"
    else
        echo "[$(date)] Failed to start notification service"
        client_pid=$(get_service_pid "client")
        server_pid=$(get_service_pid "server")
        [ -n "$client_pid" ] && kill "$client_pid" 2>/dev/null
        [ -n "$server_pid" ] && kill "$server_pid" 2>/dev/null
        # rm -f logs/client.pid logs/server.pid
        exit 1
    fi
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "fixme" ]; then
    echo "[$(date)] Starting the FIXME server..."
    nohup npm run fixme >> "$fixme_log_file" 2>&1 &
    FIXME_PID=$!
    if save_pid_with_validation "$FIXME_PID" "fixme"; then
        echo "[$(date)] FIXME service process started. [$FIXME_PID]"
        echo "[$(date)] FIXME logs at >> $fixme_log_file"
    else
        echo "[$(date)] Failed to start FIXME service"
        client_pid=$(get_service_pid "client")
        server_pid=$(get_service_pid "server")
        notification_pid=$(get_service_pid "notification")
        [ -n "$client_pid" ] && kill $client_pid 2>/dev/null
        [ -n "$server_pid" ] && kill $server_pid 2>/dev/null
        [ -n "$notification_pid" ] && kill $notification_pid 2>/dev/null
        exit 1
    fi
fi

echo "[$(date)] === Port Status ==="
if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "client" ]; then
    lsof -i :3000 >/dev/null 2>&1 && echo "✓ Port 3000 (Client) is listening" || echo "✗ Port 3000 not listening"
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "server" ]; then
    lsof -i :8000 >/dev/null 2>&1 && echo "✓ Port 8000 (Server) is listening" || echo "✗ Port 8000 not listening"
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "fixme" ]; then
    lsof -i :8001 >/dev/null 2>&1 && echo "✓ Port 8001 (Fixme) is listening" || echo "✗ Port 8001 not listening"
fi

echo "[$(date)] All background processes started!"

if [ "$DEBUG" = "true" ]; then
    echo "[$(date)] Debug mode is ON"
    echo "[$(date)] Waiting for services to initialize..."
    sleep 7

    echo "[$(date)] === Recent Logs ==="
    for service in client server notification fixme; do
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
        for service in "${services[@]}"; do
            pid_file="logs/${service}.pid"
            if [ -f "$pid_file" ]; then
                pids_str=$(cat "$pid_file")
                for pid in $pids_str; do
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
                done
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
            
            for service in "${services[@]}"; do
                pid_file="logs/${service}.pid"
                if [ -f "$pid_file" ]; then
                    pids_str=$(cat $pid_file)
                    for pid in $pids_str; do
                        if kill -0 "$pid" 2>/dev/null; then
                            services_running=$((services_running + 1))
                        else
                            echo "[$(date)] WARNING: $service (PID: $pid) has stopped unexpectedly"
                            rm -f "$pid_file"
                        fi
                    done
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
    echo "[$(date)] Services running in background"
    echo "[$(date)] Services started successfully:"
    echo "  - Client: http://localhost:3000"
    echo "  - Server: http://localhost:8000"
    echo "  - FixMe: http://localhost:8001"
    echo "[$(date)] Use 'npm run stop' to stop services"
    echo "[$(date)] Use 'npm run healthcheck' to check service health"

    exit 0
fi
