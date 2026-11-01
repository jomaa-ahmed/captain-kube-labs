#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
cat <<'EOF' | kubectl apply -f - >/dev/null
apiVersion: v1
kind: Pod
metadata:
  name: hungry
spec:
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--vm", "1", "--vm-bytes", "150M", "--vm-hang", "1"]
    resources:
      limits:
        memory: 100Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: giant
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    resources:
      requests:
        cpu: "64"
EOF
for i in $(seq 90); do
  [ "$(kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null)" -ge 1 ] 2>/dev/null && break
  sleep 2
done
touch /tmp/finished
