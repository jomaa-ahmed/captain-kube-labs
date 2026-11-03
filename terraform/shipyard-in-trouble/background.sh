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
    mkdir -p $R/boss && cd $R/boss
    cat > main.tf <<'HCL'
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    random = { source = "hashicorp/random" }
  }
}

resource "random_pet" "ship" {}

resource "local_file" "cargo" {
  filename = "${path.module}/cargo.txt"
  content  = "Ship: ${random_pet.ship.id}"
}
HCL

    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['id'] for r in d['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/boss_pet
    # the faults: a stricter constraint than the lock, a nested block written with =, messy spacing, drift
    cat > main.tf <<'HCL'
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4.0"
    }
    random = { source = "hashicorp/random" }
  }
}

resource "random_pet" "ship" {}

resource "local_file" "cargo" {
    filename = "${path.module}/cargo.txt"
  content = "Ship: ${random_pet.ship.id}"

  lifecycle = {
    create_before_destroy = true
  }
}
HCL

    rm -f cargo.txt
touch /tmp/finished
