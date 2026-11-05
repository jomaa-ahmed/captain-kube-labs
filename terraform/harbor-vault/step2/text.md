Dev and prod will use different vaults, and a backend block can't use variables. Use **partial configuration**:

- the `backend "local"` block stays, but **without** `path`
- the path goes in a file `vault.tfbackend`: `path = "vault/terraform.tfstate"`
- run `terraform init` with that file. Same state, nothing rebuilt, plan: **No changes**

<br>

<details><summary>💡 Hint</summary>

`backend "local" {}` in backend.tf, then `terraform init -reconfigure -backend-config=vault.tfbackend`. The state stays where it is because the path is the same.

</details>

<details><summary>Solution</summary>

```plain
cd /root/harbor
printf 'terraform {\n  backend "local" {}\n}\n' > backend.tf
echo 'path = "vault/terraform.tfstate"' > vault.tfbackend
terraform init -reconfigure -backend-config=vault.tfbackend -input=false
terraform plan
```{{exec}}

</details>
