#!/bin/bash
[ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.26" ] || exit 1
[ "$(kubectl get deploy cargo -o jsonpath='{.status.readyReplicas}')" = "3" ] || exit 1
kubectl get deploy cargo -o jsonpath='{.metadata.uid}' > /root/.cargo-uid
