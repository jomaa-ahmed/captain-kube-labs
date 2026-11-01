#!/bin/bash
helm list -n market --deployed -q | grep -qx shop || exit 1
d=$(kubectl get deploy -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].metadata.name}')
[ -n "$d" ] || exit 1
[ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.replicas}')" = "3" ] || exit 1
[ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.template.metadata.labels.team}')" = "harbor" ] || exit 1
[ "$(kubectl get svc -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].spec.type}')" = "NodePort" ] || exit 1
v=$(helm get values shop -n market -o yaml)
echo "$v" | grep -qE '^replicaCount: 3$' || exit 1
echo "$v" | grep -q 'NodePort' || exit 1
