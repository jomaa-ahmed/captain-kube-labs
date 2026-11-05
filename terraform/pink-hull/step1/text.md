Someone wrote `painted pink` into `hull.txt` by hand. The blueprint is right: put the hull back
**the Terraform way**. Read the plan first: what does Terraform want to do, and why?

<br>

<details><summary>💡 Hint</summary>

`terraform plan` shows the drift (the local provider treats the changed file as gone), `terraform apply` rebuilds it from the code. Not `-refresh-only`: that would accept the pink hull.

</details>

<details><summary>Solution</summary>

```plain
cd /root/pink
terraform plan
terraform apply -auto-approve
```{{exec}}

</details>
