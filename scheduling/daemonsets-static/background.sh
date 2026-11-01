#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
cat > /etc/kubernetes/manifests/ghost.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: ghost
  namespace: default
spec:
  containers:
  - name: ghost
    image: busybox:1.36
    command: ["sleep", "1d"]
EOF
for i in $(seq 90); do
  kubectl get pod ghost-controlplane >/dev/null 2>&1 && break
  sleep 2
done
touch /tmp/finished
