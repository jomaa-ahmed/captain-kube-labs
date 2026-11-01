#!/bin/bash
[ "$(kubectl get deploy beacon -o jsonpath='{.status.readyReplicas}')" = "2" ] || exit 1
[ "$(kubectl get deploy beacon -o jsonpath='{.spec.template.spec.terminationGracePeriodSeconds}')" = "15" ] || exit 1
kubectl get deploy beacon -o jsonpath='{.metadata.annotations}' | grep -q 'last-applied-configuration' || exit 1
