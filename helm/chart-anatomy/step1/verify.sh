#!/bin/bash
v=$(sed -n 's/^version: *//p' /root/charts/harbor-web/Chart.yaml | tr -d '"[:space:]')
r=$(sed -n 's/^replicaCount: *//p' /root/charts/harbor-web/values.yaml | tr -d '[:space:]')
[ "$(tr -d '[:space:]' < /root/chart-version.txt 2>/dev/null)" = "$v" ] || exit 1
[ "$(tr -d '[:space:]' < /root/replicas.txt 2>/dev/null)" = "$r" ] || exit 1
