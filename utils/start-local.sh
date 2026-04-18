#!/bin/bash

source ./utils/env-loader.sh

echo "Starting development environment..."

concurrently "cd client && npm run dev" "cd server && bash start.sh main true" "cd fixme && bash start.sh fixme"
