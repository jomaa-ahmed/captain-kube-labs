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
    mkdir -p $R/audit && cd $R/audit
    cat > versions.tf <<'HCL'
terraform {
  required_providers {
    local = {
      source = "hashicorp/local"
    }
    random = {
      source = "hashicorp/random"
    }
  }
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "hull" {
  filename = "${path.module}/hull.txt"
  content  = "oak, 3 masts"
}

resource "local_file" "logbook" {
  filename = "${path.module}/logbook.txt"
  content  = "every voyage"
}
HCL

    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    touch -d @1577836800 hull.txt 2>/dev/null || true
    cat > main.tf <<'HCL'
resource "local_file" "main_hull" {
  filename = "${path.module}/hull.txt"
  contnet  = "oak, 3 masts"
}
HCL

touch /tmp/finished
