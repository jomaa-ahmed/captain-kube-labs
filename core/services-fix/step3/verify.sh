#!/bin/bash
[ "$(kubectl get svc api -o jsonpath='{.spec.type}')" = "ClusterIP" ] || exit 1
kubectl exec client -- wget -qO- -T 3 http://api 2>/dev/null | grep -q 'Welcome to nginx' || exit 1
