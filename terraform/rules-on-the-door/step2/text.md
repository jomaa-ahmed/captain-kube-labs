Now `init` complains about the **backend**. Fix it so the ledger is kept at
`/root/rules/ledger/shipyard.tfstate`, then `init` and `apply`.

⛔ Keep the `local` backend and its `path`. ⛔ The variable `state_path` may stay, but the backend can't use it.

<br>

<details><summary>💡 Hint</summary>

The terraform block is read before any variable exists: `Variables may not be used here`. Write the path as a fixed string.

</details>

<details><summary>Solution</summary>

```plain
cd /root/rules
sed -i 's#path = var.state_path#path = "ledger/shipyard.tfstate"#' terraform.tf
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
