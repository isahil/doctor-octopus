#!/bin/bash
echo "Restarting notification service..."
npm run stop:notification
nohup npm run notification >> ../logs/notification.log 2>&1 &
NOTIFICATION_PID=$!

echo $NOTIFICATION_PID > ../logs/notification.pid
