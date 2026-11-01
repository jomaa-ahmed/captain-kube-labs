#!/bin/bash
sleep 2
kubectl -n shipyard create deployment welders --image=nginx:1.27 --replicas=6 >/dev/null
