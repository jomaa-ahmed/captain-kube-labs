#!/bin/bash
n=$(kubectl get nodes --no-headers | wc -l)
[ "$(kubectl get ds lamp -o jsonpath='{.status.desiredNumberScheduled}')" = "$n" ] || exit 1
[ "$(kubectl get ds lamp -o jsonpath='{.status.numberReady}')" = "$n" ] || exit 1
