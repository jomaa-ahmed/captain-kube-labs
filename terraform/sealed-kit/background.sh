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
    mkdir -p $R/sealed/modules/dock && cd $R/sealed
    cat > modules/dock/variables.tf <<'HCL'
variable "name" {
  type = string
}
HCL
cat > modules/dock/main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/dock-${var.name}.txt"
  content  = "${var.env}: ${var.name}"
}
HCL
cat > modules/dock/outputs.tf <<'HCL'
output "file" {
  value = local_file.this.filename
}
HCL
cat > main.tf <<'HCL'
variable "env" {
  type    = string
  default = "prod"
}

module "kestrel" {
  source = "./modules/dock"
  name   = "kestrel"
}
HCL

    terraform init -input=false >/dev/null 2>&1 || true
touch /tmp/finished
