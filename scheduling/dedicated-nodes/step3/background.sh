#!/bin/bash
sleep 2
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gold-batch
spec:
  replicas: 4
  selector:
    matchLabels: {app: gold-batch}
  template:
    metadata:
      labels: {app: gold-batch}
    spec:
      tolerations:
      - key: team
        operator: Equal
        value: gold
        effect: NoSchedule
      containers:
      - name: nginx
        image: nginx:1.27
EOF
