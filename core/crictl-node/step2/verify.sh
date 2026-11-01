#!/bin/bash
full=$(kubectl get pod lighthouse -o jsonpath='{.status.containerStatuses[0].containerID}' | sed 's#.*://##')
got=$(tr -d '[:space:]' < /root/container-id.txt 2>/dev/null)
[ ${#got} -ge 12 ] || exit 1
case "$full" in "$got"*) exit 0 ;; *) exit 1 ;; esac
