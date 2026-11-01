#!/bin/bash
[ "$(kubectl get deploy cargo -o jsonpath='{.metadata.uid}')" = "$(cat /root/.cargo-uid 2>/dev/null)" ] || exit 1
[ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
rev=$(kubectl get deploy cargo -o jsonpath='{.metadata.annotations.deployment\.kubernetes\.io/revision}')
[ "${rev:-0}" -ge 4 ] || exit 1
# the broken ReplicaSet must still exist (history kept) and be scaled to 0
broken=$(kubectl get rs -l app=cargo -o jsonpath='{range .items[*]}{.spec.template.spec.containers[0].image} {.spec.replicas}{"\n"}{end}' | grep '1.27-broken')
[ -n "$broken" ] || exit 1
echo "$broken" | grep -qv ' 0$' && exit 1
kubectl rollout status deployment/cargo --timeout=5s >/dev/null 2>&1 || exit 1
