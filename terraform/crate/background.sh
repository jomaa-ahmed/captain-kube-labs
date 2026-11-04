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
    mkdir -p $R/crate && cd $R/crate
    cat > variables.tf <<'HCL'
variable "notes" {
  type = map(string)
  default = {
    "hull.txt" = "Oak, tarred twice"
    "mast.txt" = "Pine, 20 m"
    "sail.txt" = "Canvas, patched"
  }
}
HCL
cat > main.tf <<'HCL'
data "archive_file" "crate" {
  type        = "zip"
  output_path = "${path.module}/crate.zip"

  source {
    filename = "hull.txt"
    content  = var.notes["hull.txt"]
  }
  source {
    filename = "mast.txt"
    content  = var.notes["mast.txt"]
  }
}

output "crate_size" {
  value = data.archive_file.crate.output_size
}
HCL

    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
touch /tmp/finished
