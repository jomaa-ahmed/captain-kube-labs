#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl create namespace market >/dev/null
kubectl create namespace docks >/dev/null
kubectl -n market create deployment shop --image=nginx:1.27 >/dev/null
kubectl -n market expose deployment shop --port=80 >/dev/null
kubectl -n market label svc shop app=shop --overwrite >/dev/null
cat > /root/.buyer.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: buyer
  namespace: docks
spec:
  selector:
    matchLabels: {app: buyer}
  template:
    metadata:
      labels: {app: buyer}
    spec:
      containers:
      - name: buyer
        image: busybox:1.36
        env:
        - name: SHOP_URL
          value: http://shop
        command: ["sh", "-c", "while true; do if wget -qO- -T 2 $SHOP_URL >/dev/null 2>&1; then echo OK reached shop; else echo FAIL cannot reach $SHOP_URL; fi; sleep 3; done"]
EOF
kubectl apply -f /root/.buyer.yaml >/dev/null && rm /root/.buyer.yaml
kubectl -n market wait --for=condition=Available deploy/shop --timeout=300s >/dev/null
kubectl -n docks wait --for=condition=Available deploy/buyer --timeout=300s >/dev/null
touch /tmp/finished
