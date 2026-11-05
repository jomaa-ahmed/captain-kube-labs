In `main.tf`, call the dock module as **`kestrel`** with `name = "kestrel"` and `masts = 3`, and apply.

`dock-kestrel.txt` must say `kestrel: 3 masts`, and the state must list `module.kestrel.local_file.this`.

<br>

<details><summary>💡 Hint</summary>

`module "kestrel" { source = "./modules/dock"  name = "kestrel"  masts = 3 }`. A new module call needs `terraform init` first.

</details>

<details><summary>Solution</summary>

```plain
cd /root/kit
cat > main.tf <<'HCL'
module "kestrel" {
  source = "./modules/dock"
  name   = "kestrel"
  masts  = 3
}
HCL
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
