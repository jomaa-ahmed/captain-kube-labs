#!/bin/bash
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.zone}')" = "east" ] || exit 1
            a=$(kubectl get deploy analytics -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]}')
            echo "$a" | grep -q '"key":"zone"' || exit 1
            echo "$a" | grep -q '"operator":"In"' || exit 1
            echo "$a" | grep -q 'east' && echo "$a" | grep -q 'west' || exit 1
            [ -z "$(kubectl -n default get deploy analytics -o jsonpath='{.spec.template.spec.nodeName}')" ] || exit 1
[ "$(kubectl -n default get deploy analytics -o jsonpath='{.status.readyReplicas}')" = "$(kubectl -n default get deploy analytics -o jsonpath='{.spec.replicas}')" ] || exit 1
nodes=$(kubectl -n default get pods -l app=analytics --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u)
[ "$nodes" = "node01" ] || exit 1
