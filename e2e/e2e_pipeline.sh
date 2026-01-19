#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Doctor Octopus End-to-End Test Pipeline Started..."

# Function to run test and log
run_test() {
    local name=$1
    local command=$2
    echo "Running $name..."
    eval $command
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ $name PASSED${NC}"
    elif [ $exit_code -eq 1 ]; then
        echo -e "${RED}❌ $name FAILED${NC}"
    else
        echo -e "${YELLOW}⚠️ $name ERROR (exit code $exit_code)${NC}"
    fi
    echo ""
}

START_TIME=$(date +%s)
echo "Doctor Octopus End-to-End Test Pipeline START TIME: [$(date)]"

# Run tests in order
run_test "unit:client" "npm run unit:client"
run_test "unit:server" "npm run unit:server"
run_test "api:regression" "npm run api:regression"
run_test "ui:regression" "npm run ui:regression"
run_test "perf:cards-ui" "npm run perf:cards-ui"
run_test "perf:cards-api" "npm run perf:cards-api"
run_test "perf:fixme-ws" "npm run perf:fixme-ws"

END_TIME=$(date +%s)
TIME_TAKEN=$(($END_TIME - $START_TIME))
echo "Pipeline END TIME: [$(date)]"
echo "Doctor Octopus End-to-End Test Pipeline Completed. Total TIME TAKEN: $TIME_TAKEN seconds"
