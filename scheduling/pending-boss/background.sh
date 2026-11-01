#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl taint nodes controlplane node-role.kubernetes.io/control-plane:NoSchedule- >/dev/null 2>&1 || true
kubectl taint nodes node01 maintenance=true:NoSchedule >/dev/null
kubectl create namespace dock >/dev/null
cat > /root/.boss.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata: {name: alpha, namespace: dock}
spec:
  selector: {matchLabels: {app: alpha}}
  template:
    metadata: {labels: {app: alpha}}
    spec:
      nodeSelector: {disktype: ssd}
      containers: [{name: nginx, image: "nginx:1.27"}]
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: bravo, namespace: dock}
spec:
  selector: {matchLabels: {app: bravo}}
  template:
    metadata: {labels: {app: bravo}}
    spec:
      nodeSelector: {kubernetes.io/hostname: node01}
      containers: [{name: nginx, image: "nginx:1.27"}]
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: charlie, namespace: dock}
spec:
  selector: {matchLabels: {app: charlie}}
  template:
    metadata: {labels: {app: charlie}}
    spec:
      containers:
      - name: nginx
        image: "nginx:1.27"
        resources: {requests: {cpu: "64"}}
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: delta, namespace: dock}
spec:
  selector: {matchLabels: {app: delta}}
  template:
    metadata: {labels: {app: delta}}
    spec:
      schedulerName: night-pilot
      containers: [{name: nginx, image: "nginx:1.27"}]
EOF
kubectl apply -f /root/.boss.yaml >/dev/null && rm /root/.boss.yaml
for d in alpha bravo charlie delta; do kubectl -n dock get deploy $d -o jsonpath='{.metadata.uid}' > /root/.uid-$d; done
touch /tmp/finished
