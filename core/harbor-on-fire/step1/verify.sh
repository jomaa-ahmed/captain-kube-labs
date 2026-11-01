#!/bin/bash
[ "$(kubectl -n harbor get svc harbor-web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.harbor-svc-uid)" ] || exit 1
[ "$(kubectl -n harbor get deploy harbor-web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.harbor-deploy-uid)" ] || exit 1
[ "$(kubectl -n harbor get deploy harbor-web -o jsonpath='{.status.readyReplicas}')" = "2" ] || exit 1
ip=$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.clusterIP}')
port=$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.ports[0].port}')
curl -s -m 3 "http://$ip:$port" | grep -q 'Welcome to nginx' || exit 1
