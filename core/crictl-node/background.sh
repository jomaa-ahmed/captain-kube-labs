#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
[ -f /etc/crictl.yaml ] || echo 'runtime-endpoint: unix:///run/containerd/containerd.sock' > /etc/crictl.yaml
kubectl run lighthouse --image=nginx:1.27 >/dev/null
kubectl wait --for=condition=Ready pod/lighthouse --timeout=300s >/dev/null
touch /tmp/finished
