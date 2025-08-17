
scripts_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
parent_dir="$(cd "$scripts_dir/.." && pwd)"
echo "Scripts directory: $scripts_dir"
echo "Parent directory: $parent_dir"
options=("1. commands" "2. logs" "3. exit")
echo "Choose an option to run:"
for option in "${options[@]}"; do
    echo "  $option"
done

read -p "Choose the option to run (1-2): " option

case $option in
  1)
    commands=("1. start" "2. stop" "3. restart" "4. setup" "5. pull" "6. exit")
    echo "Choose a command to run:"
    for cmd in "${commands[@]}"; do
        echo "  $cmd"
    done
    read -p "Choose the option to run (1-6): " cmd
        case $cmd in
            "1")
                echo "Starting...[npm run start]"
                npm run start-prod
                break
                ;;
            "2")
                echo "Stopping...[npm run stop]"
                npm run stop
                break
                ;;
            "3")
                echo "Restarting...[npm run restart]"
                npm run restart
                break
                ;;
            "4")
                echo "Setting up...[npm run setup]"
                npm run setup
                break
                ;;
            "5")
                echo "Pulling...[npm run pull]"
                npm run pull
                break
                ;;
            "6")
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Invalid command"
                ;;
        esac
    ;;
  2)
    echo "Running logs..."
    npm run log
    ;;
  3)
    echo "Exiting..."
    exit 0
    ;;
  *)
    echo "Invalid option"
    ;;
esac