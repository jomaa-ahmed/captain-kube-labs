#!/bin/bash
grep -lq 'name: ghost' /etc/kubernetes/manifests/* 2>/dev/null && exit 1
kubectl get pod ghost-controlplane >/dev/null 2>&1 && exit 1
exit 0
