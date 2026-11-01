#!/bin/bash
want=$(kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l)
[ "$(tr -d '[:space:]' < /root/prod-frontend.txt 2>/dev/null)" = "$want" ] || exit 1
