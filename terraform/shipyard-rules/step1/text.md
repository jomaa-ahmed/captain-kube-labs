Make dock replacements **create the new dock first**, then destroy the old one.

Then set the default of `build` to `"v2"` in `variables.tf` and apply. Check with
`terraform plan -var build=v3`: it must show `+/- create replacement and then destroy`.

<br>

<details><summary>💡 Hint</summary>

`lifecycle { create_before_destroy = true }` inside `terraform_data.dock`. Lifecycle values must be literals.

</details>

<details><summary>Solution</summary>

```plain
cd /root/rules
sed -i 's|  triggers_replace = var.build|&\n\n  lifecycle {\n    create_before_destroy = true\n  }|' main.tf
sed -i 's/default = "v1"/default = "v2"/' variables.tf
terraform apply -auto-approve
terraform plan -var build=v3
```{{exec}}

</details>
