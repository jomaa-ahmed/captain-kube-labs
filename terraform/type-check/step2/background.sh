#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/types
cat >> variables.tf <<'HCL'

variable "ship" {
  type = object({ name = string, masts = number, flag = string })
}
HCL
cat > terraform.tfvars <<'HCL'
ship = {
  name  = "Kestrel"
  masts = 2
}
HCL
cat >> main.tf <<'HCL'

resource "local_file" "flag" {
  filename = "${path.module}/flag.txt"
  content  = "${var.ship.name} flies ${var.ship.flag}"
}
HCL
sed -i 's/^         //' variables.tf main.tf terraform.tfvars
md5sum terraform.tfvars | cut -d' ' -f1 > /tmp/order_md5
