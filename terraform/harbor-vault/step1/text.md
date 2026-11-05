Add this backend to the configuration and **migrate** the existing state into it:

```
terraform {
  backend "local" {
    path = "vault/terraform.tfstate"
  }
}
```

Nothing may be rebuilt: `random_pet.ship` must keep its name. When the vault holds the state, delete the
old `terraform.tfstate` (and its backup) from the folder. The plan must end with **No changes**.

<br>

<details><summary>💡 Hint</summary>

`terraform init -migrate-state` copies the state (answer `yes`, or add `-force-copy`). `-reconfigure` would start the new backend empty.

</details>

<details><summary>Solution</summary>

```plain
cd /root/harbor
cat > backend.tf <<'HCL'
terraform {
  backend "local" {
    path = "vault/terraform.tfstate"
  }
}
HCL
terraform init -migrate-state -force-copy -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform state list
```{{exec}}

</details>
