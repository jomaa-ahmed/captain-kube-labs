#!/bin/bash
[ "$(kubectl get pod giant -o jsonpath='{.spec.containers[0].resources.requests.cpu}')" = "250m" ] || exit 1
[ "$(kubectl get pod giant -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
