#!/bin/bash
[ "$(kubectl get pod ferry -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
[ "$(kubectl get pod ferry -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27-alpine" ] || exit 1
