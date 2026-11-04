#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
if ! command -v terraform >/dev/null 2>&1; then
  curl -fsSLo /tmp/tf.zip https://releases.hashicorp.com/terraform/1.12.2/terraform_1.12.2_linux_amd64.zip
  $PY -c "import zipfile; zipfile.ZipFile('/tmp/tf.zip').extractall('/usr/local/bin')"
  chmod +x /usr/local/bin/terraform
  grep -q TF_PLUGIN_CACHE_DIR /root/.bashrc 2>/dev/null || echo 'export TF_PLUGIN_CACHE_DIR=/root/.terraform.d/plugin-cache' >> /root/.bashrc
fi
    mkdir -p $R/two && cd $R/two
    cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "dev"
}

variable "ship" {
  type    = string
  default = "Kestrel"
}

variable "yard" {
  type    = string
  default = "dock"
}

variable "dock_number" {
  type    = number
  default = 7
}
HCL
cat > main.tf <<'HCL'
locals {
  masts = 1
}

resource "local_file" "ship" {
  filename = "${path.module}/ship.txt"
  content  = "${var.ship} (${var.env}) masts: ${local.masts}"
}
HCL
cat > outputs.tf <<'HCL'
output "dock_code" {
  value = "${var.yard}-${var.dock_number}"
}
HCL

    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
touch /tmp/finished
