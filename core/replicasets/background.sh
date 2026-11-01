#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
cat > /root/.rs.yaml <<'EOF'
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: crew
spec:
  replicas: 3
  selector:
    matchLabels: {app: crew}
  template:
    metadata:
      labels: {app: crew}
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
---
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: deckhands
spec:
  replicas: 2
  selector:
    matchLabels: {app: deckhands}
  template:
    metadata:
      labels: {app: deckhands}
    spec:
      containers:
      - name: nginx
        image: nginx:1.27-tpyo
EOF
kubectl apply -f /root/.rs.yaml >/dev/null && rm /root/.rs.yaml
kubectl get rs deckhands -o jsonpath='{.metadata.uid}' > /root/.deckhands-uid
kubectl wait --for=condition=Ready pod -l app=crew --timeout=300s >/dev/null
touch /tmp/finished
