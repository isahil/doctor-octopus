#!/bin/bash

echo "Killing processes on ports 3000 and 8000..."

# Find and kill processes on port 3000 (client)
CLIENT_PIDS=$(lsof -ti:3000)
if [ ! -z "$CLIENT_PIDS" ]; then
    echo "Found processes on port 3000:"
    for pid in $CLIENT_PIDS; do
        echo "Killing client process (PID: $pid)"
        kill -9 $pid
    done
else
    echo "No processes found running on port 3000"
fi

# Find and kill processes on port 8000 (server)
SERVER_PIDS=$(lsof -ti:8000)
if [ ! -z "$SERVER_PIDS" ]; then
    echo "Found processes on port 8000:"
    for pid in $SERVER_PIDS; do
        echo "Killing server process (PID: $pid)"
        kill -9 $pid
    done
else
    echo "No processes found running on port 8000"
fi

echo "Done killing all processes"