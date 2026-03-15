# Load environment variables
echo "Loading environment variables from .env file..."
if [ -f /app/.env ]; then
    set -a
    source /app/.env
    set +a
elif [ -f .env ]; then
    set -a
    source .env
    set +a
fi
echo "Environment variables loaded successfully!"
