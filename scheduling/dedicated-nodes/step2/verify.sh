#!/bin/bash
            kubectl get deploy gold-app -o jsonpath='{.spec.template.spec.tolerations[*].key}' | grep -qw team || exit 1
            kubectl get deploy gold-app -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution}' | grep -q '"key":"team"' || exit 1
            [ -z "$(kubectl -n default get deploy gold-app -o jsonpath='{.spec.template.spec.nodeName}')" ] || exit 1
[ "$(kubectl -n default get deploy gold-app -o jsonpath='{.status.readyReplicas}')" = "$(kubectl -n default get deploy gold-app -o jsonpath='{.spec.replicas}')" ] || exit 1
nodes=$(kubectl -n default get pods -l app=gold-app --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u)
[ "$nodes" = "node01" ] || exit 1
