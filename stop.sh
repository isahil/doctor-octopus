#!/bin/bash

echo "Killing the client and server processes ..."
# Find and kill processes on port 3000 (client)
# CLIENT_PIDS=$(lsof -ti:3000)
# if [ ! -z "$CLIENT_PIDS" ]; then
#     echo "Found processes on port 3000:"
#     for pid in $CLIENT_PIDS; do
#         echo "Killing client process (PID: $pid)"
#         kill -9 $pid
#     done
# else
#     echo "No processes found running on port 3000"
# fi

# Find and kill processes on port 8000 (server)
kill_processes_on_port() {
    local port=$1
    local process_type=$2
    echo "Looking for ($process_type) processes on port #$port ..."
    
    local PIDS=$(lsof -ti:$port)
    if [ ! -z "$PIDS" ]; then
        echo "Found processes on port $port:"
        for pid in $PIDS; do
            echo "Killing $process_type process (PID: $pid)"
            kill -9 $pid
        done
    else
        echo "No processes found running on port $port"
    fi
}

# Call the function for server port
kill_processes_on_port 3000 "client"
kill_processes_on_port 8000 "server-main"
kill_processes_on_port 8001 "server-notification"
kill_processes_on_port 8002 "server-fixme"

echo "Done killing all the running processes!"
