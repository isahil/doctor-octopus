# Set default value for lines (10 if not provided)
#!/bin/bash
lines=${1:-10}
# Get the directory where the script is located
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
root=".."
directory="$( cd "$script_dir/.." && pwd )"
# If the script is in a subdirectory, adjust accordingly
# Example: directory="$( cd "$script_dir/.." && pwd )"
options=("server" "client" "notification")

# Display options with numbers
echo "Available log types:"
for i in "${!options[@]}"; do
    echo "  $((i+1)). ${options[$i]}"
done

# Read user selection
read -p "Choose log type (1-${#options[@]}): " selection

# Convert selection to array index and get value
if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#options[@]}" ]; then
    LOG_TYPE=${options[$((selection-1))]}
    echo "tailing log file for: $LOG_TYPE"
else
    echo "Invalid selection"
    exit 1
fi

tail -f -n $lines $directory/logs/$LOG_TYPE.log
