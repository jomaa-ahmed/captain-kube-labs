The output `dock_code` prints `dock-7`. The harbor wants **`DOCK-007`**: capitals, and the number padded
to three digits.

Build it in a local named **`dock_code`** from `var.yard` and `var.dock_number`, output that local, and apply.
With `dock_number = 42` it must give `DOCK-042`.

⛔ Terraform has no functions of your own: combine the built-in ones.

<br>

<details><summary>💡 Hint</summary>

`format("%s-%03d", var.yard, var.dock_number)` pads the number; wrap it in `upper(...)`. Test it: `terraform console -var dock_number=42`, then `local.dock_code`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/two
cat >> main.tf <<'HCL'

locals {
  dock_code = upper(format("%s-%03d", var.yard, var.dock_number))
}
HCL
sed -i 's|value = .*|value = local.dock_code|' outputs.tf
terraform apply -var env=prod -auto-approve
terraform output -raw dock_code
```{{exec}}

</details>
