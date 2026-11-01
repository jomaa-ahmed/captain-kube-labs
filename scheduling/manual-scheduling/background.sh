#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
mkdir -p /etc/kubernetes/parked
mv /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/parked/
for i in $(seq 60); do
  [ -z "$(kubectl -n kube-system get pods -l component=kube-scheduler -o name 2>/dev/null)" ] && break
  sleep 2
done
kubectl run cargo --image=nginx:1.27 >/dev/null
touch /tmp/finished
