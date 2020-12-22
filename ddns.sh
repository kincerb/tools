#!/bin/bash
# set path & umask for script
case ":$PATH:" in
    *:/sbin:*)
        umask 022
        ;;
    *)
        PATH=/sbin:/usr/sbin:/usr/local/sbin:$PATH ; export PATH ; umask 022
        ;;
esac
ip_file=/jbod/google/logs/ddns/devslash.me.lastip
log_file=/jbod/google/logs/ddns/devslash.me.log
stamp=$(date +%m-%d-%y)
agent=Lynx
# If we can't ping a google DNS server, we probably aren't connected to the internet
# and there would be no sense in continuing
if ! ( ping -q -W 2 -c3 8.8.8.8 &>/dev/null ); then
  echo "${stamp}  Error: Not connected to the outside world." >> "${log_file}"
  exit 1
fi

if [ ! -e "${ip_file}" ]; then
    echo "${stamp}  Error: ${ip_file} doesn't exist." >> "${log_file}"
fi

current_ip=$(wget -qO- http://ip.changeip.com 2>/dev/null |head -1 |grep -Po "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

if /bin/true; then
    curl https://"${DDNS_DEVSLASH_USER}":"${DDNS_DEVSLASH_PASSWORD}"@domains.google.com/nic/update?hostname=home.devslash.me\&myip="${current_ip}" \
        -X GET \
        -H "HTTP/1.1 Host: ${HOSTNAME} Authorization: Basic base64-encoded-auth-string" \
        -A "${agent}" \
        -q &>/dev/null

    echo -e "${stamp} IP for home.devslash.me was updated to ${current_ip}" > "${log_file}"
    echo "${current_ip}" > "${ip_file}"
fi
