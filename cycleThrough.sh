#!/bin/bash
#set -x

shopt -s expand_aliases
alias tmux='tmux -S /var/tmux/shared'

script=$(basename $0)

cycle() {
    session="${1}"
    shift 1
    windows=$(tmux lsw -F '#I#F' -t"${session}")
    windowCount=$(echo "${windows}" |wc -l)
    for x in ${windows}; do
        if [[ "${x}" == *'*'* ]]; then
            currentWin="${x%%[*]}"
            break
        fi
    done
    currentWin="${currentWin:-1}"

    for window in $(seq "${windowCount}" -1 1); do
        tmux selectw -t"${session}:+"
        sleep "${waitTime}"
    done
}

printHelp() {
    cat <<EOF >&2

Usage: ${script} [OPTION]

This script cycles through all windows in tmux session
           
Example:
    ${script} -s zEast-tcp -w 3     # Cycles through zEast-tcp, waits 3 seconds on each window

EOF
    exit 0
}

#---------------------------------
# Here's where the magic happens  |
#---------------------------------
while :; do
    case $1 in
        -h|--help|-\?)
            printHelp
            exit 0;;
        -s|--session)
            sessionString="${2}"; shift 2;;
        -w|--wait)
            waitTime="${2}"; shift 2;;
        --) # End of all options
            shift; break;;
        -*)
            say Error "Unknown option (ignored): $1" >&2
            shift;;
        *) # No more options
            break;;
    esac
done

waitTime="${waitTime:-0.5}"

# Main
if [ ! -z "${sessionString}" ]; then
    # If "all", run loop for each session found
    if [ "${sessionString}" == "all" ]; then
        targetSessions=$(tmux ls -F '#S' 2>/dev/null |xargs)
    # session ends with a splat, we need to find matching session names
    elif [[ "${sessionString}" =~ [*]$ ]]; then
        sessionString="${sessionString%%[*]}"
        targetSessions=$(tmux ls -F '#S' 2>/dev/null |grep -i "${sessionString}.*" |xargs)
    else
        targetSessions="${sessionString}"
    fi
# As long as we're in TMUX, we didn't need a session provided, we'll just run
# wherever we are connected
elif [ ! -z "${TMUX}" ]; then
    targetSessions=$(tmux display -p '#S')
else
    say Error "Must provide a session name when not currently connected"
    exit 3
fi

if [ -z "${targetSessions}" ]; then
    say Error "Could not find valid TMUX sessions"
    exit 4
fi

for x in ${targetSessions}; do
    cycle "${x}" &
done

