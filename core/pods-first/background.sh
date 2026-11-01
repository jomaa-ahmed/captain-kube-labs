#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
kubectl run ferry --image=nginx:1.27-alpne >/dev/null
touch /tmp/finished
