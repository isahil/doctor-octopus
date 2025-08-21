#!/bin/bash
SERVICE=$1

echo "Restarting $SERVICE service..."
npm run stop:$SERVICE
nohup npm run $SERVICE >> ./logs/$SERVICE.log 2>&1 &
SERVICE_PID=$!

echo $SERVICE_PID > ../logs/$SERVICE.pid
