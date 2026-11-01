#!/bin/bash
[ "$(kubectl get svc web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.web-uid)" ] || exit 1
ip=$(kubectl get svc web -o jsonpath='{.spec.clusterIP}')
port=$(kubectl get svc web -o jsonpath='{.spec.ports[0].port}')
curl -s -m 3 "http://$ip:$port" | grep -q 'Welcome to nginx' || exit 1
