#!/bin/bash
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.size}')" = "large" ] || exit 1
            kubectl get deploy reports -o jsonpath='{.spec.template.spec.affinity.nodeAffinity}' | grep -q '"key":"size"' || exit 1
            [ -z "$(kubectl -n default get deploy reports -o jsonpath='{.spec.template.spec.nodeName}')" ] || exit 1
[ "$(kubectl -n default get deploy reports -o jsonpath='{.status.readyReplicas}')" = "$(kubectl -n default get deploy reports -o jsonpath='{.spec.replicas}')" ] || exit 1
nodes=$(kubectl -n default get pods -l app=reports --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u)
[ "$nodes" = "node01" ] || exit 1
