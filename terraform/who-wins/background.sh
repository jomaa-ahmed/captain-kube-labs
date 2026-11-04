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
    mkdir -p $R/wins && cd $R/wins
    cat > variables.tf <<'HCL'
variable "flag" {
  type    = string
  default = "default"
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "flag" {
  filename = "${path.module}/flag.txt"
  content  = var.flag
}
HCL

    echo 'flag = "tfvars"' > terraform.tfvars
    echo 'flag = "a-auto"' > a.auto.tfvars
    echo 'flag = "z-auto"' > z.auto.tfvars
    echo 'flag = "prod"' > prod.tfvars
    md5sum *.tf *.tfvars > /tmp/wins_md5
    terraform init -input=false >/dev/null
touch /tmp/finished
