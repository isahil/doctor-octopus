#!/bin/bash
DEBUG=$1

echo "[$(date)] Starting background processes for Doctor Octopus app..."

echo "[$(date)] Starting the client server..."
nohup npm run client >> logs/client.log 2>&1 &
CLIENT_PID=$!
echo "[$(date)] Client started with PID: [$CLIENT_PID]"

echo "[$(date)] Starting the main server..."
nohup npm run server >> logs/server.log 2>&1 &
SERVER_PID=$!
echo "[$(date)] Main server started with PID: [$SERVER_PID]"

echo "[$(date)] Starting the notification server..."
nohup npm run notification >> logs/notification.log 2>&1 &
NOTIFICATION_PID=$!
echo "[$(date)] Notification server started with PID: [$NOTIFICATION_PID]"

# echo "Starting fixme service..."
# nohup npm run fixme >> logs/fixme.log 2>&1 &
# FIXME_PID=$!
# echo "Fixme service started with PID: [$FIXME_PID]"

echo "[$(date)] Client server started with PID: [$CLIENT_PID]" > logs/client.log
echo "[$(date)] Main server started with PID: [$SERVER_PID]" > logs/server.log
echo "[$(date)] Notification server started with PID: [$NOTIFICATION_PID]" > logs/notification.log
echo $CLIENT_PID > logs/client.pid
echo $SERVER_PID > logs/server.pid
echo $NOTIFICATION_PID > logs/notification.pid
echo "[$(date)] All background processes started!"

if [ "$DEBUG" = "true" ]; then
    echo "[$(date)] Debug mode is ON"
    # Add after starting processes
    echo "[$(date)] Checking if services are accessible..."
    sleep 7

    # Check if ports are listening
    lsof -ti :3000 || echo "Port 3000 not listening"
    lsof -ti :8000 || echo "Port 8000 not listening"
    lsof -ti :8001 || echo "Port 8001 not listening"

    # Check process status
    ps aux | grep -E "(npm|uvicorn|python)" || echo "No processes found"

    # Check logs
    echo "=== Client Log ==="
    tail -10 logs/client.log
    echo "=== Client Log ==="
    echo "=== Notification Log ==="
    tail -10 logs/notification.log
    echo "=== Notification Log ==="
    echo "=== Server Log ==="
    tail -10 logs/server.log
    echo "=== Server Log ==="
    wait
fi
