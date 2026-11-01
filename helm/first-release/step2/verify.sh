#!/bin/bash
want=$(kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
[ -n "$want" ] || exit 1
got=$(tr -d '[:space:]' < /root/deployment.txt 2>/dev/null)
[ "$got" = "$want" ] || exit 1
