#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl run radar-1 --image=registry.k8s.io/pause:3.10 --labels=env=prod,tier=frontend,team=red >/dev/null
kubectl run radar-2 --image=registry.k8s.io/pause:3.10 --labels=env=prod,tier=backend,team=red >/dev/null
kubectl run radar-3 --image=registry.k8s.io/pause:3.10 --labels=env=prod,tier=frontend,team=blue >/dev/null
kubectl run sonar-1 --image=registry.k8s.io/pause:3.10 --labels=env=dev,tier=frontend,team=blue >/dev/null
kubectl run sonar-2 --image=registry.k8s.io/pause:3.10 --labels=env=dev,tier=backend,team=red >/dev/null
kubectl run sonar-3 --image=registry.k8s.io/pause:3.10 --labels=env=staging,tier=frontend,team=red >/dev/null
kubectl run mast-1 --image=registry.k8s.io/pause:3.10 --labels=env=staging,tier=backend,team=blue >/dev/null
kubectl run mast-2 --image=registry.k8s.io/pause:3.10 --labels=env=prod,tier=backend,team=blue >/dev/null
kubectl run mast-3 --image=registry.k8s.io/pause:3.10 --labels=tier=frontend,team=red >/dev/null

    kubectl create service clusterip radar --tcp=80:80 >/dev/null
    kubectl set selector svc radar tier=frontend >/dev/null
    kubectl get svc radar -o jsonpath='{.metadata.uid}' > /root/.radar-uid
    kubectl wait --for=condition=Ready pod --all --timeout=300s >/dev/null
touch /tmp/finished
