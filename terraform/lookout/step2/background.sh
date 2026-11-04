#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
cd $R/lookout
cat > launch.tf <<'HCL'
resource "terraform_data" "launch" {
  provisioner "local-exec" {
    command = "exit 1"
  }
}
HCL
sed -i 's/^         //' launch.tf
terraform apply -auto-approve -input=false >/dev/null 2>&1 || true
