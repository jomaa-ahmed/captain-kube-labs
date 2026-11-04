Someone added a `random_pet` to `/root/supplier/main.tf`. Run `terraform plan` and read the error.

Fix it the right way, then apply: the state must list `random_pet.figurehead`.

⛔ Don't delete `.terraform.lock.hcl` or the `.terraform` folder.

<br>

<details><summary>💡 Hint</summary>

The error says the random provider is *required by this configuration but no version is selected*. Which command downloads providers and records them in the lock file?

</details>

<details><summary>Solution</summary>

```plain
cd /root/supplier
terraform plan || true
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
