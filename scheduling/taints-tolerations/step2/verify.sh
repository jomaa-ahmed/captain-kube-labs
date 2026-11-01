#!/bin/bash
[ "$(kubectl get pod tanker -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod tanker -o jsonpath='{.status.phase}')" = "Running" ] || exit 1

            kubectl get pod tanker -o jsonpath='{.spec.tolerations[*].key}' | grep -qw cargo || exit 1
