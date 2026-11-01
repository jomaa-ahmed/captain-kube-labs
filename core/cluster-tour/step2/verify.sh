#!/bin/bash
want=$(sed -n 's/^staticPodPath: *//p' /var/lib/kubelet/config.yaml | tr -d '[:space:]')
want=${want%/}
got=$(tr -d '[:space:]' < /root/manifests.txt 2>/dev/null); got=${got%/}
[ -n "$want" ] && [ "$got" = "$want" ] || exit 1
[ "$(tr -d '[:space:]' < /root/manifests-count.txt 2>/dev/null)" = "$(ls "$want" | wc -l)" ] || exit 1
