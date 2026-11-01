#!/bin/bash
want=$(kubectl get pods -l 'env in (prod,staging),team!=red' -o custom-columns=:metadata.name --no-headers | sort)
got=$(sed 's#^pod/##; s/[[:space:]]//g' /root/selected.txt 2>/dev/null | grep . | sort)
[ -n "$want" ] && [ "$got" = "$want" ] || exit 1
