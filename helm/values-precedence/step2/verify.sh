#!/bin/bash
helm list -n market --deployed -q | grep -qx shop || exit 1
rev=$(helm list -n market --filter '^shop$' -o yaml | sed -n 's/.*revision: *"\{0,1\}\([0-9]*\).*/\1/p')
[ "${rev:-0}" -ge 2 ] || exit 1
d=$(kubectl get deploy -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].metadata.name}')
[ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.replicas}')" = "1" ] || exit 1
[ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.template.metadata.labels.team}')" = "harbor" ] || exit 1
[ "$(kubectl get svc -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].spec.type}')" = "NodePort" ] || exit 1
helm get values shop -n market -o yaml | grep -qE '^replicaCount: 1$' || exit 1
