#!/bin/bash
[ "$(tr -d '[:space:]' < /root/node-critical.txt 2>/dev/null)" = "$(kubectl get pc system-node-critical -o jsonpath='{.value}')" ] || exit 1
