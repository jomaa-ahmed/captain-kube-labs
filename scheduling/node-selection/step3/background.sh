#!/bin/bash
sleep 2
kubectl label nodes node01 size=large --overwrite >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reports
spec:
  replicas: 2
  selector:
    matchLabels: {app: reports}
  template:
    metadata:
      labels: {app: reports}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: size
                operator: In
                values: [Large]
      containers:
      - name: nginx
        image: nginx:1.27
EOF
