#!/bin/bash
[ "$(kubectl get deploy cargo -o jsonpath='{.metadata.uid}')" = "$(cat /root/.cargo-uid 2>/dev/null)" ] || exit 1
[ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
rev=$(kubectl get deploy cargo -o jsonpath='{.metadata.annotations.deployment\.kubernetes\.io/revision}')
[ "${rev:-0}" -ge 4 ] || exit 1
# one ReplicaSet per version (1.26, 1.27, broken): the undo reuses the 1.27 one
[ "$(kubectl get rs -l app=cargo --no-headers | wc -l)" = "3" ] || exit 1
kubectl rollout status deployment/cargo --timeout=5s >/dev/null 2>&1 || exit 1
