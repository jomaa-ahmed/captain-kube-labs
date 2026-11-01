#!/bin/bash
[ "$(kubectl get pod cargo -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod cargo -o jsonpath='{.status.phase}')" = "Running" ] || exit 1

            [ "$(kubectl get pod cargo -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
