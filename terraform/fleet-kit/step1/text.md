Create **`modules/mast`** (variables `name` and `masts`, the resource, an output `file`) and call it **once**
with `for_each = var.fleet` (the map is in `variables.tf`). Keep the same filenames and contents.

The three files must **not be rebuilt**, and no `local_file` block may stay in the root. Plan: **No changes**.

<br>

<details><summary>💡 Hint</summary>

Module resource: `local_file "this"` with `filename = "${path.root}/mast-${var.name}.txt"`, `content = "${var.name}: ${var.masts} masts"`. Root: `module "mast" { source = "./modules/mast"  for_each = var.fleet  name = each.key  masts = each.value }`. Then a moved block per file: `from = local_file.mast_kestrel  to = module.mast["kestrel"].local_file.this`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/fleet
mkdir -p modules/mast
cat > modules/mast/variables.tf <<'HCL'
variable "name" {
  type        = string
  description = "Ship name"
}

variable "masts" {
  type        = number
  description = "Number of masts"
}
HCL
cat > modules/mast/main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/mast-${var.name}.txt"
  content  = "${var.name}: ${var.masts} masts"
}
HCL
cat > modules/mast/outputs.tf <<'HCL'
output "file" {
  value = local_file.this.filename
}
HCL
cat > main.tf <<'HCL'
module "mast" {
  source   = "./modules/mast"
  for_each = var.fleet
  name     = each.key
  masts    = each.value
}

moved {
  from = local_file.mast_kestrel
  to   = module.mast["kestrel"].local_file.this
}

moved {
  from = local_file.mast_osprey
  to   = module.mast["osprey"].local_file.this
}

moved {
  from = local_file.mast_wren
  to   = module.mast["wren"].local_file.this
}
HCL
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
