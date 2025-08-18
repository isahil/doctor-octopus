
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
root=".."
directory="$( cd "$script_dir/.." && pwd )"

alias DO="cd \"$directory\" && npm run prompt"
