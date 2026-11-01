#!/bin/bash
[ "$(tr -d '[:space:]' < /root/lighthouse-key.txt 2>/dev/null)" = "/registry/pods/default/lighthouse" ] || exit 1
