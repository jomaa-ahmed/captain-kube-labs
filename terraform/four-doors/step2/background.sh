#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/doors
mkdir -p hull.txt/old
cat >> main.tf <<'HCL'

resource "local_file" "hull" {
  filename = "${path.module}/hull.txt"
  content  = "oak"
}
HCL
sed -i 's/^         //' main.tf
