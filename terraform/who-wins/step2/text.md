Apply so that `flag.txt` says **prod**.

⛔ Don't edit, rename or delete any `.tf` or `.tfvars` file, and don't create new ones.

<br>

<details><summary>💡 Hint</summary>

prod.tfvars never loads on its own. Pass it on the command line: `terraform apply -var-file=prod.tfvars`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/wins
terraform apply -var-file=prod.tfvars -auto-approve
```{{exec}}

</details>
