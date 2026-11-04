#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/timber
touch -d @1577836800 hull.txt 2>/dev/null || true
md5sum *.tf > /tmp/timber_md5
