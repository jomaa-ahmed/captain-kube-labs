#!/bin/bash
[ "$(kubectl get pod parcel -o jsonpath='{.spec.schedulerName}')" = "default-scheduler" ] || exit 1
[ "$(kubectl get pod parcel -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
