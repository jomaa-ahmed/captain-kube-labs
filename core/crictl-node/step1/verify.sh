#!/bin/bash
want=$(crictl version 2>/dev/null | awk '/RuntimeName/{print $2}')
[ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/runtime.txt 2>/dev/null)" = "$want" ] || exit 1
