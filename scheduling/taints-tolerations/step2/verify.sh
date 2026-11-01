#!/bin/bash
[ "$(kubectl get pod tanker -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod tanker -o jsonpath='{.status.phase}')" = "Running" ] || exit 1

            kubectl get pod tanker -o jsonpath='{range .spec.tolerations[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qxE 'cargo=(hazardous)?:(NoSchedule)?' || exit 1
