In `/root/layout`:
- the `terraform` block goes into **terraform.tf**
- the resource goes into **main.tf**
- the output goes into **outputs.tf**
- `all.tf` is gone

Then `terraform fmt -check` must pass and `terraform validate` must say Success.

<br>

<details><summary>💡 Hint</summary>

File names don't matter to Terraform, only to people. `terraform fmt` fixes the spacing for you.

</details>

<details><summary>Solution</summary>

```plain
cd /root/layout
cat > terraform.tf <<'HCL'
terraform {
  required_providers {
    local = { source = "hashicorp/local" }
  }
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = "Crew of the shipyard"
}
HCL
cat > outputs.tf <<'HCL'
output "crew_file" {
  value = local_file.crew.filename
}
HCL
rm all.tf
terraform fmt
terraform init
terraform validate
```{{exec}}

</details>
