#!/bin/bash
h='{.spec.hard.pods} {.spec.hard.requests\.cpu} {.spec.hard.limits\.memory}'
[ "$(kubectl -n shipyard get quota cap -o jsonpath="$h")" = "5 1 2Gi" ] || exit 1
