#!/bin/bash
r='{.spec.containers[0].resources}'
[ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.requests.cpu}')" = "100m" ] || exit 1
[ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.requests.memory}')" = "64Mi" ] || exit 1
[ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.limits.cpu}')" = "200m" ] || exit 1
[ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.limits.memory}')" = "128Mi" ] || exit 1
[ "$(kubectl get pod crane -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
