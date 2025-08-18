#!/bin/bash

echo "[$(date)] Killing the client and server processes ..."

kill_processes_on_port() {
    local port=$1
    local process_type=$2
    echo "[$(date)] Looking for ($process_type) processes on port #$port ..."
    
    local PIDS=$(lsof -ti:$port)
    if [ ! -z "$PIDS" ]; then
        echo "[$(date)] Found processes on port $port:"
        for pid in $PIDS; do
            echo "[$(date)] Killing $process_type process (PID: $pid)"
            kill -9 $pid
        done
    else
        echo "[$(date)] No processes found running on port $port"
    fi
}

# Call the function for application ports to kill
kill_processes_on_port 3000 "client"
kill_processes_on_port 8000 "server-main"
kill_processes_on_port 8001 "server-fixme"
# kill_processes_on_port 8001 "server-notification"

echo "[$(date)] Done killing all the running processes!"
