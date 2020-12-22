#!/usr/local/bin/bash
tmux new -d -c ~/ -s main
tmux selectw -t main:1
tmux splitw -h -p 50 -t main:1
tmux neww -t main:
tmux neww -t main:
tmux neww -t main:
tmux selectw -t main:1
tmux selectp -t 1
tmux rename-window -t main:1 "|"
tmux setw -q -t main:1 allow-rename off
tmux -2 attach-session -t main
