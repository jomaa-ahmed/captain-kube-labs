#!/bin/bash
[ "$(kubectl get svc web-lb -o jsonpath='{.spec.type}')" = "LoadBalancer" ] || exit 1
np=$(kubectl get svc web-lb -o jsonpath='{.spec.ports[0].nodePort}')
[ -n "$np" ] || exit 1
[ "$(tr -d '[:space:]' < /root/lb-nodeport.txt 2>/dev/null)" = "$np" ] || exit 1
ext=$(kubectl get svc web-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}{.status.loadBalancer.ingress[0].hostname}')
got=$(tr -d '[:space:]<>' < /root/lb-external.txt 2>/dev/null | tr 'A-Z' 'a-z')
[ "$got" = "${ext:-pending}" ] || exit 1
curl -s -m 3 "http://localhost:$np" | grep -q 'Welcome to nginx' || exit 1
