#!/bin/bash
[ "$(kubectl get deploy cargo -o jsonpath='{.metadata.uid}')" = "$(cat /root/.cargo-uid 2>/dev/null)" ] || exit 1
[ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
kubectl rollout status deployment/cargo --timeout=5s >/dev/null 2>&1 || exit 1
