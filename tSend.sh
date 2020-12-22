#!/bin/bash
#set -x

shopt -s expand_aliases
source "${HOME}"/.config/bash.d/functions.sh
source "${HOME}"/.config/bash.d/aliases.sh

script=$(basename $0)

sendKeys() {
    if ("${diag}"); then
        echo "Matched:"
        echo "-------"
        for pane in ${targetPanes}; do
            echo "  ${pane}"
        done
    else
        for pane in ${targetPanes}; do
            tmux send-keys -t"${pane}" "$@"
        done
    fi
}

findSessions() {
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
        return 1
    fi

    if [ -z "${targetSessions}" ]; then
        say Error "Could not find valid TMUX sessions"
        return 1
    fi
}

findPanes() {
    for session in ${targetSessions}; do
        if [ -z "${paneString}" ]; then
            targetPanes="${targetPanes} $(tmux lsp -s -F '#S:#I.#P' -t ${session} |xargs)"
        else
            while read -r x; do
                paneUID="${x%%__*}"
                paneCMD="${x##*__}"
                if [[ "${paneCMD}" == *${paneString}* ]]; then
                    targetPanes="${targetPanes} ${paneUID}"
                fi
            done < <(tmux lsp -s -F '#S:#I.#P__#{pane_current_command}' -t ${session})
        fi
    done

    if [ -z "${targetPanes}" ]; then
        say Error "Could not find any panes started with: ${paneString}"
        return 1
    else
        return 0
    fi
}

printHelp() {
    cat <<EOF >&2

Usage: ${script} [OPTION]

This script sends keys to all windows in a tmux session, or certain windows
           
Example:
    ${script} -s dce -p c3270 'c-z' 'l'     # Sends keys to panes matching "c3270" in session "dce"
    ${script} 'C-z l'                       # Sends keys to all panes
    ${script} 'df -h' 'C-m'                 # Sends df -h command and hits ENTER

EOF
    exit 0
}

#---------------------------------
# Here's where the magic happens  |
#---------------------------------

diag="false"

while :; do
    case $1 in
        -d|--diag)
            diag="true"; shift 1;;
        -h|--help|-\?)
            printHelp
            exit 0;;
        -s|--session)
            sessionString="${2}"; shift 2;;
        -p|--panes)
            paneString="${2}"; shift 2;;
        --) # End of all options
            shift; break;;
        -*)
            say Error "Unknown option (ignored): $1" >&2
            shift;;
        *) # No more options
            break;;
    esac
done

# The rest of the arguments should be the keys to send
if [ "$#" -eq 0 ] && ! ("${diag}"); then
    printHelp
fi

# Main
for func in findSessions findPanes; do
    if ! ${func}; then
        exit 5
    fi
done

sendKeys "$@"
