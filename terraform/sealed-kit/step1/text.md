Make the module use the **root's** `var.env`: `dock-kestrel.txt` must say `prod: kestrel` and change with the
root's value (`terraform plan -var env=dev` must want to change it). Apply.

<br>

<details><summary>💡 Hint</summary>

Declare `variable "env" { type = string }` in modules/dock/variables.tf (no default), and pass `env = var.env` in the module block.

</details>

<details><summary>Solution</summary>

```plain
cd /root/sealed
printf '\nvariable "env" {\n  type = string\n}\n' >> modules/dock/variables.tf
sed -i 's|  name   = "kestrel"|  name   = "kestrel"\n  env    = var.env|' main.tf
terraform apply -auto-approve
```{{exec}}

</details>
