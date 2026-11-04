The ledger must survive any `terraform destroy`. Seal it so Terraform **refuses** to destroy it, and apply.

Check: `terraform plan -destroy` must stop with `Instance cannot be destroyed`.

<br>

<details><summary>💡 Hint</summary>

`lifecycle { prevent_destroy = true }` inside `local_file.ledger`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/rules
sed -i 's|  content  = "every ship we ever built"|&\n\n  lifecycle {\n    prevent_destroy = true\n  }|' main.tf
terraform apply -auto-approve
terraform plan -destroy || true
```{{exec}}

</details>
