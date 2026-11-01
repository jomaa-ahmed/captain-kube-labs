#!/bin/bash
[ "$(tr -d '[:space:]' < /root/good-revision.txt 2>/dev/null)" = "1" ] || exit 1
