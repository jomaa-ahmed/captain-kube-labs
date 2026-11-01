#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: parcel
spec:
  schedulerName: night-pilot
  containers:
  - name: nginx
    image: nginx:1.27
EOF
touch /tmp/finished
