#!/bin/bash
[ "$(kubectl get pod signal -o jsonpath='{.spec.containers[*].name}')" = "web logger" ] || exit 1
[ "$(kubectl get pod signal -o jsonpath='{.status.containerStatuses[*].ready}')" = "true true" ] || exit 1
kubectl logs signal -c logger --tail=5 2>/dev/null | grep -q ahoy || exit 1
