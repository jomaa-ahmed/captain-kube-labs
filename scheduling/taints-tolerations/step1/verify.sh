#!/bin/bash
kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\n"}{end}' | grep -qx 'cargo=hazardous:NoSchedule' || exit 1
