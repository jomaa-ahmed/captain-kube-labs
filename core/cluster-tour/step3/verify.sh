#!/bin/bash
[ "$(tr -d '[:space:]' < /root/not-a-pod.txt 2>/dev/null | tr 'A-Z' 'a-z')" = "kubelet" ] || exit 1
want=$(ps -o args= -C kubelet | grep -o -- '--config=[^ ]*' | head -1 | cut -d= -f2)
[ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/kubelet-config.txt 2>/dev/null)" = "$want" ] || exit 1
