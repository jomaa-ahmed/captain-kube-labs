#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl create deployment web --image=nginx:1.27 --replicas=2 >/dev/null
kubectl create deployment api --image=nginx:1.27 >/dev/null
kubectl create service clusterip web --tcp=80:8080 >/dev/null
kubectl patch svc web -p '{"spec":{"selector":{"app":"wbe"}}}' >/dev/null
kubectl get svc web -o jsonpath='{.metadata.uid}' > /root/.web-uid
kubectl run client --image=busybox:1.36 -- sleep 1d >/dev/null
kubectl wait --for=condition=Available deploy/web deploy/api --timeout=300s >/dev/null
kubectl wait --for=condition=Ready pod/client --timeout=300s >/dev/null
touch /tmp/finished
