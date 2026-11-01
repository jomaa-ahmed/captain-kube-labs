#!/bin/bash
h='{.spec.hard.pods} {.spec.hard.requests\.cpu} {.spec.hard.limits\.memory}'
[ "$(kubectl -n shipyard get quota cap -o jsonpath="$h")" = "8 1 2Gi" ] || exit 1
[ "$(kubectl -n shipyard get deploy welders -o jsonpath='{.status.readyReplicas}')" = "6" ] || exit 1
