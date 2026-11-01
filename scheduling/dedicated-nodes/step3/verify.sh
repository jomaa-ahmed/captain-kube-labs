#!/bin/bash
            kubectl get deploy gold-batch -o jsonpath='{.spec.template.spec.tolerations[*].key}' | grep -qw team || exit 1
            kubectl rollout status deploy/gold-batch --timeout=5s >/dev/null 2>&1 || exit 1
            [ "$(kubectl -n default get deploy gold-batch -o jsonpath='{.status.readyReplicas}')" = "$(kubectl -n default get deploy gold-batch -o jsonpath='{.spec.replicas}')" ] || exit 1
nodes=$(kubectl -n default get pods -l app=gold-batch --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | sort -u)
[ "$nodes" = "node01" ] || exit 1
