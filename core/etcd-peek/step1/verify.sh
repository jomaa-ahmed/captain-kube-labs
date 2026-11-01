#!/bin/bash
want=$(grep -o -- '--trusted-ca-file=[^ ]*' /etc/kubernetes/manifests/etcd.yaml | head -1 | cut -d= -f2)
[ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/etcd-ca.txt 2>/dev/null)" = "$want" ] || exit 1
