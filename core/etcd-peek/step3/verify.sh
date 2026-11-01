#!/bin/bash
want=$(kubectl get deploy -n kube-system --no-headers 2>/dev/null | wc -l)
[ "$(tr -d '[:space:]' < /root/deploy-count.txt 2>/dev/null)" = "$want" ] || exit 1
