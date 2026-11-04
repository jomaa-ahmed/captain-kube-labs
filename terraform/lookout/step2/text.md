Someone added `launch.tf`: a `terraform_data.launch` with a `local-exec` provisioner. The apply failed.

Run `terraform plan` and read what Terraform now thinks of `terraform_data.launch`. Then fix the
command (make it `echo launched`) and apply, so the plan ends with **No changes**.

⛔ `terraform untaint` alone hides the problem: the command would still fail next time.

<br>

<details><summary>💡 Hint</summary>

A failed creation-time provisioner marks the resource **tainted**, so the next apply replaces it. Fix the command in launch.tf, then `terraform apply`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/lookout
sed -i 's/command = "exit 1"/command = "echo launched"/' launch.tf
terraform apply -auto-approve
```{{exec}}

</details>
