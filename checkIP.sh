#!/bin/bash

if [[ -f /tmp/iplist ]]; then
    rm /tmp/iplist
fi

net_rep=0
echo "Network Representation:"
echo "  1. CIDR"
echo "  2. IP range"
until [[ $net_rep -eq 1 ]] || [[ $net_rep -eq 2 ]]; do
    echo -n "> Please input your choice (default 1): "
    read net_rep
    [[ ! -n "$net_rep" ]] && net_rep=1
done

case $net_rep in
    1)
        while [[ 1 -eq 1 ]]; do
            read -p "> Network: " net
            if [[ $net =~ ^([0-9]{1,2}|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]{1,2}|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]{1,2}|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]{1,2}|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\/([1-9]|[1-2][0-9]|3[0-2])$ ]]; then
                net=${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}
                break
            else
                echo "Illegal network: $net. Please input again."
                continue
            fi
        done
    ;;
esac
echo "Available ip:"
for host in `seq 100 254`; do
{
    ip=$net.$host
    ping -w 2 -c 1 $ip > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "$ip" >> /tmp/iplist
    fi
} &
done
sleep 4
[[ -f /tmp/iplist ]] && cat /tmp/iplist | sort -n | awk '{
    if (NR % 5 != 0) {
        printf $0
        printf "    "
    }
    else
        print $0
}'
echo
echo -n "Total "
if [[ -f /tmp/iplist ]]; then
    wc -l /tmp/iplist
else
    echo 0
fi
