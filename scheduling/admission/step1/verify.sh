#!/bin/bash
want=$(grep -o -- '--enable-admission-plugins=[^ ]*' /root/.apiserver-orig.yaml | head -1 | cut -d= -f2)
[ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/plugins.txt 2>/dev/null)" = "$want" ] || exit 1
