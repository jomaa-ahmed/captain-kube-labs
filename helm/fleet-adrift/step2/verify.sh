#!/bin/bash
helm list -n armada --deployed -q | grep -qx beacon || exit 1
bh=$(helm history beacon -n armada --max 100)
echo "$bh" | grep -q 'Install complete' || exit 1
echo "$bh" | tail -n 1 | grep -q 'Rollback to 1' || exit 1
[ "$(kubectl get svc -n armada -l app.kubernetes.io/instance=beacon -o jsonpath='{.items[0].spec.ports[0].port}')" = "80" ] || exit 1
bd=$(kubectl get deploy -n armada -l app.kubernetes.io/instance=beacon -o jsonpath='{.items[0].metadata.name}')
kubectl -n armada rollout status deploy/$bd --timeout=5s >/dev/null 2>&1 || exit 1

helm list -n armada --deployed -q | grep -qx compass || exit 1
cd=$(kubectl get deploy -n armada -l app.kubernetes.io/instance=compass -o jsonpath='{.items[0].metadata.name}')
[ "$(kubectl get deploy $cd -n armada -o jsonpath='{.spec.replicas}')" = "2" ] || exit 1
[ "$(kubectl get deploy $cd -n armada -o jsonpath='{.status.readyReplicas}')" = "2" ] || exit 1
[ "$(kubectl get deploy $cd -n armada -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27-alpine" ] || exit 1
[ "$(kubectl get deploy $cd -n armada -o jsonpath='{.spec.template.metadata.labels.tier}')" = "nav" ] || exit 1
[ "$(kubectl get svc -n armada -l app.kubernetes.io/instance=compass -o jsonpath='{.items[0].spec.type}')" = "NodePort" ] || exit 1
cv=$(helm get values compass -n armada -o yaml)
echo "$cv" | grep -q '1.27-alpine' || exit 1
echo "$cv" | grep -q 'NodePort' || exit 1
