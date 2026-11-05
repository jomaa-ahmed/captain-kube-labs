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
    mkdir -p $R/fleet && cd $R/fleet
    cat > variables.tf <<'HCL'
variable "fleet" {
  type = map(number)
  default = {
    kestrel = 3
    osprey  = 2
    wren    = 1
  }
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "mast_kestrel" {
  filename = "${path.root}/mast-kestrel.txt"
  content  = "kestrel: 3 masts"
}

resource "local_file" "mast_osprey" {
  filename = "${path.root}/mast-osprey.txt"
  content  = "osprey: 2 masts"
}

resource "local_file" "mast_wren" {
  filename = "${path.root}/mast-wren.txt"
  content  = "wren: 1 masts"
}
HCL

    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    touch -d @1577836800 mast-kestrel.txt mast-osprey.txt mast-wren.txt 2>/dev/null || true
touch /tmp/finished
