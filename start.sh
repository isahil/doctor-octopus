#!/bin/bash

echo "[$(date)] Starting Background Processes for Doctor Octopus App"

echo "[$(date)] Starting main app..."
nohup npm run start >> logs/doc.log 2>&1 &
MAIN_PID=$!
echo "[$(date)] Main app started with PID: $MAIN_PID"

echo "[$(date)] Starting notification service..."
nohup npm run notification >> logs/notification.log 2>&1 &
NOTIFICATION_PID=$!
echo "[$(date)] Notification service started with PID: $NOTIFICATION_PID"

# echo "Starting fixme service..."
# nohup npm run fixme >> logs/fixme.log 2>&1 &
# FIXME_PID=$!
# echo "Fixme service started with PID: $FIXME_PID"

echo "[$(date)] Main app started with PID: $MAIN_PID" > logs/doc.log
echo "[$(date)] Notification service started with PID: $NOTIFICATION_PID" > logs/notification.log
echo "[$(date)] Fixme service started with PID: $FIXME_PID" > logs/fixme.log

echo "[$(date)] All background processes started."
