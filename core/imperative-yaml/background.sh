#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
touch /tmp/finished
