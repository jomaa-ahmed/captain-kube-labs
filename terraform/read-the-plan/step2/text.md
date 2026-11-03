Save the plan to a file called `tfplan` in `/root/plan`, then apply **that file**.
Afterwards the plan must say *No changes*.

<br>

<details><summary>💡 Hint</summary>

`terraform plan -out=tfplan`, then `terraform apply tfplan` (no question asked).

</details>

<details><summary>Solution</summary>

```plain
cd /root/plan
terraform plan -out=tfplan
terraform apply tfplan
```{{exec}}

</details>
