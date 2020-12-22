#!/bin/bash
#set -x

xrandr --output eDP --primary

if [ -e /home/kincerb/.i3/xmodmap.i3 ]; then
    xmodmap /home/kincerb/.i3/xmodmap
fi

if [ "${HOSTNAME}" == "nw150679" ]; then
    touchpad_id=10
else
    touchpad_id=13
fi

xinput --set-prop "${touchpad_id}" "libinput Tapping Enabled" 1
xinput --set-prop "${touchpad_id}" "libinput Natural Scrolling Enabled" 1

if ! (pgrep compton &>/dev/null); then
    (compton -CGb &)
fi

# if ! (pgrep twmnd &>/dev/null); then
    # (/bin/twmnd &)
# fi

if ! (pgrep blueman-applet &>/dev/null); then 
    (blueman-applet &)
fi

if ! (pgrep nm-applet &>/dev/null); then
    (nm-applet &)
fi

# if ! (pgrep pasystray &>/dev/null); then
    # (/bin/pasystray &)
# fi

if ! (pgrep insync &>/dev/null); then
    (sleep 10; insync start &)
fi

# if ! (pgrep xautolock &>/dev/null); then
    # (xautolock -time 10 -locker "i3lock -n -c 454545 -i /home/kincerb/Pictures/arch-blue.png" &)
# fi
