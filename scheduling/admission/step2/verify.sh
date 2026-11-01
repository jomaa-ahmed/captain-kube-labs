#!/bin/bash
grep -o -- '--enable-admission-plugins=[^ ]*' /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NamespaceAutoProvision || exit 1
ps -o args= -C kube-apiserver | grep -q NamespaceAutoProvision || exit 1
kubectl get --raw=/readyz >/dev/null 2>&1 || exit 1
