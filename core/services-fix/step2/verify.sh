#!/bin/bash
[ "$(kubectl get svc web-public -o jsonpath='{.spec.type}')" = "NodePort" ] || exit 1
[ "$(kubectl get svc web-public -o jsonpath='{.spec.ports[0].nodePort}')" = "30080" ] || exit 1
curl -s -m 3 http://localhost:30080 | grep -q 'Welcome to nginx' || exit 1
