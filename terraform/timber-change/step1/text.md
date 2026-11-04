Make `local_file.hull` be **replaced** whenever `var.recipe` changes. Don't put the recipe in the hull's content.

Check: `terraform plan -var recipe=pine` must say
`local_file.hull will be replaced due to changes in replace_triggered_by`. Apply with the default (oak) at the end.

<br>

<details><summary>💡 Hint</summary>

replace_triggered_by only takes resources. Hold the value in one: `resource "terraform_data" "recipe" { input = var.recipe }`, then `replace_triggered_by = [terraform_data.recipe]` in the hull's lifecycle.

</details>

<details><summary>Solution</summary>

```plain
cd /root/timber
cat > main.tf <<'HCL'
resource "terraform_data" "recipe" {
  input = var.recipe
}

resource "local_file" "hull" {
  filename = "${path.module}/hull.txt"
  content  = "hull"

  lifecycle {
    replace_triggered_by = [terraform_data.recipe]
  }
}
HCL
terraform apply -auto-approve
terraform plan -var recipe=pine
```{{exec}}

</details>
