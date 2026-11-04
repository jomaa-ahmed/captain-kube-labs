#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/halfbuilt
terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['result'] for r in d['values']['root_module']['resources'] if r['address']=='random_password.dock_code'][0])" > /tmp/old_code 2>/dev/null
md5sum main.tf | cut -d' ' -f1 > /tmp/main_md5
