#!/bin/bash
[ "$(kubectl get rs crew -o jsonpath='{.spec.replicas}')" = "5" ] || exit 1
[ "$(kubectl get rs crew -o jsonpath='{.status.readyReplicas}')" = "5" ] || exit 1
