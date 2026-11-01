#!/bin/bash
want=$(kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}')
[ "$(tr -d '[:space:]' < /root/etcd-pod.txt 2>/dev/null)" = "$want" ] || exit 1
want=$(kubectl get pods -n kube-system -l component=kube-apiserver -o jsonpath='{.items[0].spec.nodeName}')
[ "$(tr -d '[:space:]' < /root/api-node.txt 2>/dev/null)" = "$want" ] || exit 1
