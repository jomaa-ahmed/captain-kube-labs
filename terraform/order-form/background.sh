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
    mkdir -p $R/order && cd $R/order
    printf 'Ada\nBo\nCyrus\n' > crew.txt
    md5sum crew.txt | cut -d' ' -f1 > /tmp/crew_md5
    cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "prod"
}

variable "ship" {
  type = object({ name = string, masts = number, flag = string })
}
HCL
cat > terraform.tfvars <<'HCL'
ship = {
  name  = "Kestrel"
  masts = "two"
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = ""
}

locals {
  label = "${var.env}-${var.ship.name}"
}

resource "local_file" "manifest" {
  filename = "${path.module}/manifest.txt"
  content  = "${locals.label}: ${var.ship.masts} masts, flag ${var.ship.flag}\ncrew: ${local_file.crew.content}"
}

resource "random_password" "dock_code" {
  length = 12
}
HCL
cat > outputs.tf <<'HCL'
output "label" {
  value = local.label
}

output "dock_code" {
  value = random_password.dock_code.result
}
HCL

    terraform init -input=false >/dev/null
touch /tmp/finished
