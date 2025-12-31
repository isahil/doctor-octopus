# Load environment variables
if [ -f /app/.env ]; then
    set -a
    source /app/.env
    set +a
elif [ -f .env ]; then
    set -a
    source .env
    set +a
fi
