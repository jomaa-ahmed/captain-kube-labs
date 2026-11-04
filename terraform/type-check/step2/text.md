The order in `terraform.tfvars` describes the ship with an **object**, but doesn't say the flag.
Run `terraform plan` and read the error.

Most customers don't care about the flag: make it **optional, violet by default**.
`flag.txt` must say `Kestrel flies violet`.

⛔ Don't change `terraform.tfvars`: that's the customer's order.

<br>

<details><summary>💡 Hint</summary>

In the object type: `flag = optional(string, "violet")`. The second argument is the default.

</details>

<details><summary>Solution</summary>

```plain
cd /root/types
terraform plan || true
sed -i 's/flag = string/flag = optional(string, "violet")/' variables.tf
terraform apply -auto-approve
```{{exec}}

</details>
