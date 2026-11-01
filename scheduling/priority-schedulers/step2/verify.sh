#!/bin/bash
[ "$(kubectl get pc critical-cargo -o jsonpath='{.value}')" = "1000000" ] || exit 1
[ "$(kubectl get pc critical-cargo -o jsonpath='{.globalDefault}')" != "true" ] || exit 1
[ "$(kubectl get pod medic -o jsonpath='{.spec.priority}')" = "1000000" ] || exit 1
[ "$(kubectl get pod medic -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
