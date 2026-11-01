#!/bin/bash
helm list -n fleet --deployed -q | grep -qx web || exit 1
h=$(helm history web -n fleet --max 100)
echo "$h" | grep -q 'Install complete' || exit 1
echo "$h" | tail -n 1 | grep -q 'Rollback to 1' || exit 1
helm get values web -n fleet -o yaml | grep -q 'tpyo' && exit 1
d=$(kubectl get deploy -n fleet -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
kubectl get deploy $d -n fleet -o jsonpath='{.spec.template.spec.containers[0].image}' | grep -q 'tpyo' && exit 1
kubectl -n fleet rollout status deploy/$d --timeout=5s >/dev/null 2>&1 || exit 1
exit 0
