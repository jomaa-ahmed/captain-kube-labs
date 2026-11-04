#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/blanks
cat >> variables.tf <<'HCL'

variable "masts" {
  type        = number
  description = "How many masts"
}
HCL
cat >> main.tf <<'HCL'

resource "local_file" "masts" {
  filename = "${path.module}/masts.txt"
  content  = "${var.masts} masts"
}
HCL
echo 'masts = "three"' >> terraform.tfvars
sed -i 's/^         //' variables.tf main.tf
