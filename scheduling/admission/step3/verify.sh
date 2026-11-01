#!/bin/bash
kubectl get ns frontier >/dev/null 2>&1 || exit 1
kubectl -n frontier get pod sentry >/dev/null 2>&1 || exit 1
