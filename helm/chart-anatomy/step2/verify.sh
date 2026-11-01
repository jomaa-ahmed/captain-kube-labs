#!/bin/bash
f=/root/rendered.yaml
grep -q '^kind: Deployment' $f || exit 1
grep -q '^kind: Service$' $f || exit 1
grep -q 'preview-harbor-web' $f || exit 1
[ -z "$(helm list -A -q)" ] || exit 1
kubectl get deploy -A -l app.kubernetes.io/instance=preview 2>/dev/null | grep -q preview && exit 1
exit 0
