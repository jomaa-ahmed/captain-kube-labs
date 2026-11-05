In `/root/yard8`, reach this state:
- `terraform init` succeeds, and the state lives in **`vault/terraform.tfstate`**
- no `terraform.tfstate` (or backup) is left in `/root/yard8`
- `random_pet.ship` keeps its **current name**: nothing is rebuilt that doesn't need to be
- `hull.txt` says what the blueprint says
- `terraform plan` says **No changes**
- Git ignores every state file (the folder is a repository)

<br>

<details><summary>💡 Hint</summary>

Backend blocks can't use variables. Migrate (don't reconfigure) to keep the ship. Drift is fixed by a normal apply. One .gitignore pattern covers all state files.

</details>

<details><summary>Solution</summary>

```plain
cd /root/yard8
sed -i 's|path = var.vault_path|path = "vault/terraform.tfstate"|' backend.tf
terraform init -migrate-state -force-copy -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform apply -auto-approve
printf '*.tfstate*\n.terraform/\n' > .gitignore
```{{exec}}

</details>
