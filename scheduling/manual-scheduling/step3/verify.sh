#!/bin/bash
[ -f /etc/kubernetes/manifests/kube-scheduler.yaml ] || exit 1
[ "$(kubectl -n kube-system get pods -l component=kube-scheduler -o jsonpath='{.items[0].status.containerStatuses[0].ready}')" = "true" ] || exit 1
