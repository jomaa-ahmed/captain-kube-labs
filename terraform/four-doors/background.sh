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
    mkdir -p $R/doors && cd $R/doors
    cat > main.tf <<'HCL'
resource "local_file" "orders" {
  filname = "${path.module}/orders.txt"
  content = "build 3 masts"
}

resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = local_file.log.content
}

resource "local_file" "log" {
  filename = "${path.module}/log.txt"
  content  = local_file.crew.content
}
HCL

    terraform init -input=false >/dev/null
touch /tmp/finished
