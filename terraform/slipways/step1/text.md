Change `main.tf` so the file is called `dock-<workspace>.txt` and says `masts: 3` in **prod**, `masts: 1` everywhere else.

Then create the workspaces `dev` and `prod` and apply in **each** of them.

<br>

<details><summary>💡 Hint</summary>

`terraform.workspace` holds the current name: `filename = "${path.module}/dock-${terraform.workspace}.txt"`, `content = "masts: ${terraform.workspace == "prod" ? 3 : 1}"`. Then `terraform workspace new dev`, apply, `terraform workspace new prod`, apply.

</details>

<details><summary>Solution</summary>

```plain
cd /root/slipways
cat > main.tf <<'HCL'
resource "local_file" "dock" {
  filename = "${path.module}/dock-${terraform.workspace}.txt"
  content  = "masts: ${terraform.workspace == "prod" ? 3 : 1}"
}
HCL
terraform workspace new dev
terraform apply -auto-approve
terraform workspace new prod
terraform apply -auto-approve
```{{exec}}

</details>
