Run `terraform init` in `/root/rules` and read the first error.

Fix it so this Terraform (1.12) is accepted, **keeping** a `required_version` rule that allows 1.12.x.
For now, `init` may still fail with a second error: that's the next step.

<br>

<details><summary>💡 Hint</summary>

`terraform version` shows what you run. `required_version = "~> 1.12"` allows 1.12 and newer 1.x.

</details>

<details><summary>Solution</summary>

```plain
cd /root/rules
terraform init || true
sed -i 's/required_version = ">= 1.13"/required_version = "~> 1.12"/' terraform.tf
```{{exec}}

</details>
