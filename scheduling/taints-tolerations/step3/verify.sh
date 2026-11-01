#!/bin/bash
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'cargo=hazardous:NoSchedule' || exit 1
            [ "$(kubectl get pod barge -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod barge -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
