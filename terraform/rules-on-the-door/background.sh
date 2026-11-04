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
    mkdir -p $R/rules && cd $R/rules
    cat > terraform.tf <<'HCL'
terraform {
  required_version = ">= 1.13"

  backend "local" {
    path = var.state_path
  }
}
HCL
cat > variables.tf <<'HCL'
variable "state_path" {
  type    = string
  default = "ledger/shipyard.tfstate"
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "rules" {
  filename = "${path.module}/rules.txt"
  content  = "One quill at a time."
}
HCL
touch /tmp/finished
