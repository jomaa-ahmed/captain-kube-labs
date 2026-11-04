The harbor repaints the hull whenever it likes and passes the colour in `var.paint`. Terraform must
**stop updating** the hull's `input` after it's built, but keep using `var.paint` when it creates the hull.

Check: `terraform plan -var paint=red` must say **No changes**.

<br>

<details><summary>💡 Hint</summary>

`lifecycle { ignore_changes = [input] }` inside `terraform_data.hull`. Keep `paint = var.paint` in the input.

</details>

<details><summary>Solution</summary>

```plain
cd /root/rules
sed -i 's|  input = { paint = var.paint, masts = 3 }|&\n\n  lifecycle {\n    ignore_changes = [input]\n  }|' main.tf
terraform plan -var paint=red
```{{exec}}

</details>
