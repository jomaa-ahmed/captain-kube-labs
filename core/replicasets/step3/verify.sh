#!/bin/bash
[ "$(kubectl get rs deckhands -o jsonpath='{.metadata.uid}')" = "$(cat /root/.deckhands-uid)" ] || exit 1
[ "$(kubectl get rs deckhands -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
imgs=$(kubectl get pods -l app=deckhands -o jsonpath='{range .items[*]}{.spec.containers[0].image} {.status.phase}{"\n"}{end}')
[ "$(echo "$imgs" | grep -c 'nginx:1.27 Running')" = "2" ] || exit 1
[ "$(echo "$imgs" | grep -c .)" = "2" ] || exit 1
