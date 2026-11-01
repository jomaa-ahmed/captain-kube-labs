#!/bin/bash
got=$(tr -d '[:space:]' < /root/missing.txt 2>/dev/null | tr 'A-Z' 'a-z')
[ "$got" = "kube-scheduler" ] || [ "$got" = "scheduler" ] || exit 1
