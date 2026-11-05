#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/slipways
terraform workspace new test >/dev/null 2>&1 || terraform workspace select test >/dev/null 2>&1
terraform apply -auto-approve -input=false >/dev/null 2>&1
terraform workspace select default >/dev/null 2>&1
