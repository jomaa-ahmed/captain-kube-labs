The same blueprint must now build the **prod** shipyard: every file named `shipyard-prod-...`.

⛔ Don't edit any `.tf` file. Locals can't be set from outside... but what are they built from?

<br>

<details><summary>💡 Hint</summary>

`local.prefix` is built from `var.env`, and a variable *can* come from outside: `terraform apply -var 'env=prod'`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/margin
terraform apply -var 'env=prod' -auto-approve
```{{exec}}

</details>
