#!/bin/bash
[ "$(kubectl get svc radar -o jsonpath='{.metadata.uid}')" = "$(cat /root/.radar-uid)" ] || exit 1
[ "$(kubectl get svc radar -o jsonpath='{.spec.selector.env}')" = "prod" ] || exit 1
[ "$(kubectl get svc radar -o jsonpath='{.spec.selector.tier}')" = "frontend" ] || exit 1
[ "$(kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l)" = "2" ] || exit 1
n=$(kubectl get endpointslices -l kubernetes.io/service-name=radar -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}{"\n"}{end}' | grep -c .)
[ "$n" = "2" ] || exit 1
