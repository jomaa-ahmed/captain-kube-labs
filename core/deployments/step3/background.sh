#!/bin/bash
sleep 2
kubectl set image deployment/cargo '*=nginx:1.27-broken' >/dev/null
