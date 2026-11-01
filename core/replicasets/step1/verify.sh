#!/bin/bash
p=$(tr -d '[:space:]' < /root/new-pod.txt 2>/dev/null)
[ -n "$p" ] || exit 1
[ "$(kubectl get pod "$p" -o jsonpath='{.metadata.labels.app}' 2>/dev/null)" = "crew" ] || exit 1
# the new pod must not be one of the pods that existed when the lab started
grep -qx "$p" /root/.crew-initial-pods && exit 1
# and the ReplicaSet must own it (not a hand-made pod with the same label)
[ "$(kubectl get pod "$p" -o jsonpath='{.metadata.ownerReferences[0].name}')" = "crew" ] || exit 1
exit 0
