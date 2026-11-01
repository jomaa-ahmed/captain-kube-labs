#!/bin/bash
want=$(kubectl get pod lighthouse -o jsonpath='{.status.podIP}')
[ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/pod-ip.txt 2>/dev/null)" = "$want" ] || exit 1
