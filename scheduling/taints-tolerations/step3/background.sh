#!/bin/bash
sleep 2
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: barge
spec:
  nodeSelector:
    kubernetes.io/hostname: node01
  tolerations:
  - key: cargo
    operator: Equal
    value: hazardus
    effect: NoSchedule
  containers:
  - name: nginx
    image: nginx:1.27
EOF
