#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl create namespace harbor >/dev/null
kubectl create namespace town >/dev/null
kubectl -n harbor create deployment harbor-web --image=nginx:1.27-alpinee --replicas=2 >/dev/null
kubectl -n harbor create service clusterip harbor-web --tcp=80:8080 >/dev/null
kubectl -n harbor patch svc harbor-web -p '{"spec":{"selector":{"app":"harbor-wbe"}}}' >/dev/null
kubectl -n harbor get svc harbor-web -o jsonpath='{.metadata.uid}' > /root/.harbor-svc-uid
kubectl -n harbor get deploy harbor-web -o jsonpath='{.metadata.uid}' > /root/.harbor-deploy-uid
cat > /root/.visitor.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visitor
  namespace: town
spec:
  selector:
    matchLabels: {app: visitor}
  template:
    metadata:
      labels: {app: visitor}
    spec:
      containers:
      - name: visitor
        image: busybox:1.36
        env:
        - name: TARGET
          value: http://harbor-web
        command: ["sh", "-c", "while true; do if wget -qO- -T 2 $TARGET >/dev/null 2>&1; then echo OK harbor reached; else echo FAIL cannot reach $TARGET; fi; sleep 3; done"]
EOF
kubectl apply -f /root/.visitor.yaml >/dev/null && rm /root/.visitor.yaml
kubectl -n town wait --for=condition=Available deploy/visitor --timeout=300s >/dev/null
touch /tmp/finished
