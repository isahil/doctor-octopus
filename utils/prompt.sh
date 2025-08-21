
scripts_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
parent_dir="$(cd "$scripts_dir/.." && pwd)"

options=("1. commands" "2. logs" "3. exit")
echo "Choose an option to run:"
for option in "${options[@]}"; do
    echo "  $option"
done

read -p "Choose the option to run (1-2): " option

case $option in
  1)
    commands=("1. start" "2. stop" "3. restart" "4. restart:server" "5. restart:notification" "6. restart:fixme" "7. setup" "8. pull" "9. exit")
    echo "Choose a command to run:"
    for cmd in "${commands[@]}"; do
        echo "  $cmd"
    done
    read -p "Choose the option to run (1-9): " cmd
        case $cmd in
            "1")
                echo "Starting...[npm run start]"
                npm run start:prod
                break
                ;;
            "2")
                echo "Stopping...[npm run stop]"
                npm run stop
                break
                ;;
            "3")
                echo "Restarting...[npm run restart]"
                npm run restart:prod
                break
                ;;
            "4")
                echo "Restarting...[npm run restart]"
                npm run restart:prod
                break
                ;;
            "5")
                echo "Restarting...[npm run restart]"
                npm run restart:prod
                break
                ;;
            "6")
                echo "Restarting...[npm run restart]"
                npm run restart:prod
                break
                ;;
            "7")
                echo "Setting up...[npm run setup]"
                npm run setup
                break
                ;;
            "8")
                echo "Pulling...[npm run pull]"
                npm run pull
                break
                ;;
            "9")
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