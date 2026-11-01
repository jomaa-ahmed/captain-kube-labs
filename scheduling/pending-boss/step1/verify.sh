#!/bin/bash
for d in alpha bravo charlie delta; do
  [ "$(kubectl -n dock get deploy $d -o jsonpath='{.metadata.uid}')" = "$(cat /root/.uid-$d)" ] || exit 1
  [ "$(kubectl -n dock get deploy $d -o jsonpath='{.status.readyReplicas}')" = "1" ] || exit 1
done
kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'maintenance=true:NoSchedule' || exit 1
kubectl -n dock get deploy charlie -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' | grep -q . || exit 1
