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
    mkdir -p $R/yard && cd $R/yard
    cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "prod"
}

variable "ship" {
  type    = string
  default = "Kestrel"
}

variable "crew" {
  type    = list(string)
  default = ["Ada", "Bo", "Cyrus"]
}

variable "notes" {
  type = map(string)
  default = {
    "hull.txt" = "Oak"
    "mast.txt" = "Pine"
  }
}
HCL
cat > main.tf <<'HCL'
locals {
  masts = var.env == "prod" ? 3 : 1
  flag  = var.env == "prod" ? ["violet"] : "grey"
  label = shipname(var.env, var.ship)
}

resource "local_file" "bunk" {
  for_each = var.crew
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.value}"
}

resource "local_file" "manifest" {
  filename = "${path.module}/manifest.txt"
  content  = "${local.label}: ${local.masts} masts, flag ${local.flag}"
}

data "archive_file" "crate" {
  type        = "zip"
  output_path = "${path.module}/crate.zip"

  dynamic "source" {
    for_each = var.notes
    content {
      filename = each.key
      content  = each.value
    }
  }
}
HCL
cat > outputs.tf <<'HCL'
output "bunks" {
  value = local_file.bunk[*].filename
}

output "crate_size" {
  value = data.archive_file.crate.output_size
}
HCL

    terraform init -input=false >/dev/null
touch /tmp/finished
