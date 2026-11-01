#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/.apiserver-orig.yaml
touch /tmp/finished
