#!/bin/bash
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'cargo=hazardous:NoSchedule' || exit 1
            # the barge needs the right papers: nodeName alone would sneak past a NoSchedule taint
            kubectl get pod barge -o jsonpath='{range .spec.tolerations[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qxE 'cargo=(hazardous)?:(NoSchedule)?' || exit 1
            [ "$(kubectl get pod barge -o jsonpath='{.spec.nodeName}')" = "node01" ] || exit 1
[ "$(kubectl get pod barge -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
