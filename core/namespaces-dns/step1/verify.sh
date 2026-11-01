#!/bin/bash
[ "$(kubectl config view --minify -o jsonpath='{..namespace}')" = "market" ] || exit 1
