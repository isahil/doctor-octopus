#!/bin/bash
PROCESS=$1
PROCESS_TARGET=${PROCESS:-all}

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

kill_process_with_pid() {
    echo "[$(date)] Killing process with PID file"
    local process=$1
    directory="./logs"
    file="$directory/$process.pid"
    if [ -f "$file" ]; then
        pid=$(cat "$file")
        echo "[$(date)] Killing $process (PID: $pid)"
        kill -9 $pid
    else
        echo "[$(date)] No PID file found for $file"
    fi
}

if [ "$PROCESS_TARGET" == "all" ]; then
    echo "[$(date)] Killing all the client and server processes ..."
    # Call the function for application ports to kill
    kill_processes_on_port 3000 "client"
    kill_processes_on_port 8000 "server"
    kill_processes_on_port 8001 "server-fixme"
    kill_process_with_pid "notification"
else
    echo "[$(date)] Killing specific process: $PROCESS_TARGET"
    kill_process_with_pid "$PROCESS_TARGET"
fi

echo "[$(date)] Done killing the running process/es!"
