#!/bin/bash

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
