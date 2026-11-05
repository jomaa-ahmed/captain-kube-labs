Call it as module **`label`** from the registry, pinned to exactly version **`0.24.1`**, with
`namespace = "sy"`, `stage = "prod"`, `name = "kestrel"`. Add a root output **`id`** = the module's `id`, and apply.

`terraform output -raw id` must print `sy-prod-kestrel`.

<br>

<details><summary>💡 Hint</summary>

`module "label" { source = "cloudposse/label/null"  version = "0.24.1" ... }` and `output "id" { value = module.label.id }`. Then init and apply.

</details>

<details><summary>Solution</summary>

```plain
cd /root/sources
cat > main.tf <<'HCL'
module "label" {
  source    = "cloudposse/label/null"
  version   = "0.24.1"
  namespace = "sy"
  stage     = "prod"
  name      = "kestrel"
}

output "id" {
  value = module.label.id
}
HCL
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
