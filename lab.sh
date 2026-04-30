source "$HOME/Programming/Calcpad/.venv/bin/activate"

nohup jupyter lab --port=8900 --notebook-dir="$HOME/Programming/Calcpad/" & disown

exit
