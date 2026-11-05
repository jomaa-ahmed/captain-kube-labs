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
    mkdir -p $R/kityard/modules/dock && cd $R/kityard
    cat > modules/dock/variables.tf <<'HCL'
variable "name" {
  type        = string
  description = "Ship name"
}

variable "masts" {
  type    = number
  default = 1
}
HCL
cat > modules/dock/main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/dock-${var.name}.txt"
  content  = "${var.name}: ${var.masts} masts"
}
HCL
cat > modules/dock/outputs.tf <<'HCL'
output "file" {
  value = local_file.this.filename
}
HCL
cat > main.tf <<'HCL'
variable "label_source" {
  type    = string
  default = "cloudposse/label/null"
}

module "dock" {
  source  = "./modules/dock"
  version = "1.0.0"
  masts  = 3
}

module "label" {
  source  = var.label_source
  version   = "0.25.0"
  namespace = "sy"
  stage     = "prod"
  name      = "kestrel"
}

output "dock_file" {
  value = module.dock.local_file.this.filename
}

output "label_id" {
  value = module.label.id
}
HCL

touch /tmp/finished
