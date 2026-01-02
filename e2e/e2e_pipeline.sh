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

# Run tests in order
run_test "unit:client" "npm run unit:client"
run_test "unit:server" "npm run unit:server"
run_test "api:regression" "npm run api:regression"
run_test "ui:regression" "npm run ui:regression"
run_test "perf:cards" "npm run perf:cards"
run_test "perf:fixme" "npm run perf:fixme"

echo "Doctor Octopus End-to-End Test Pipeline Completed."