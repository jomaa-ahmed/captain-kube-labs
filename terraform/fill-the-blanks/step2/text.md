The customer also ordered masts. Someone added a `masts` variable (a **number**) and filled in the order...
Run `terraform plan` and read the error.

Fix it so `masts.txt` says `3 masts`. ⛔ `masts` must stay a `number`.

<br>

<details><summary>💡 Hint</summary>

`a number is required`: the order says `"three"`. Write the value as a number in terraform.tfvars: `masts = 3`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/blanks
terraform plan || true
sed -i 's/masts = "three"/masts = 3/' terraform.tfvars
terraform apply -auto-approve
```{{exec}}

</details>
