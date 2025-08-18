#!/bin/bash
echo "Restarting notification service..."
nohup npm run restart:notification >> logs/notification.log 2>&1 &
NOTIFICATION_PID=$!

echo $NOTIFICATION_PID > logs/notification.pid
