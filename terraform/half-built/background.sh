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
    mkdir -p $R/halfbuilt && cd $R/halfbuilt
    echo "another crew's notes" > logs
    cat > main.tf <<'HCL'
resource "random_pet" "ship" {}

resource "random_password" "dock_code" {
  length = 16
}

resource "local_file" "logbook" {
  filename = "${path.module}/logs/today.txt"
  content  = "Ship ${random_pet.ship.id} launched"
}
HCL

    terraform init -input=false >/dev/null
    terraform apply -auto-approve -input=false >/dev/null 2>&1 || true
    terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['id'] for r in d['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/pet_id
touch /tmp/finished
