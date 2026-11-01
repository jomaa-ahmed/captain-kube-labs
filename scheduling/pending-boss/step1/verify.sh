#!/bin/bash
for d in alpha bravo charlie delta; do
  [ "$(kubectl -n dock get deploy $d -o jsonpath='{.metadata.uid}')" = "$(cat /root/.uid-$d)" ] || exit 1
  [ "$(kubectl -n dock get deploy $d -o jsonpath='{.status.readyReplicas}')" = "1" ] || exit 1
  # nodeName in the template would skip the scheduler and every rule in this lab
  [ -z "$(kubectl -n dock get deploy $d -o jsonpath='{.spec.template.spec.nodeName}')" ] || exit 1
done
node_of() { kubectl -n dock get pods -l app=$1 --field-selector=status.phase=Running -o jsonpath='{.items[0].spec.nodeName}'; }
kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'maintenance=true:NoSchedule' || exit 1
# alpha keeps its nodeSelector and lands on an ssd node
[ "$(kubectl -n dock get deploy alpha -o jsonpath='{.spec.template.spec.nodeSelector.disktype}')" = "ssd" ] || exit 1
[ "$(kubectl get node "$(node_of alpha)" -o jsonpath='{.metadata.labels.disktype}')" = "ssd" ] || exit 1
# bravo keeps its node pin and runs on node01, past the taint
[ "$(kubectl -n dock get deploy bravo -o jsonpath='{.spec.template.spec.nodeSelector.kubernetes\.io/hostname}')" = "node01" ] || exit 1
[ "$(node_of bravo)" = "node01" ] || exit 1
# charlie keeps a (sensible) CPU request
kubectl -n dock get deploy charlie -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' | grep -q . || exit 1
# delta is scheduled by the real scheduler
s=$(kubectl -n dock get deploy delta -o jsonpath='{.spec.template.spec.schedulerName}')
[ -z "$s" ] || [ "$s" = "default-scheduler" ] || exit 1
