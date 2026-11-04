Now remove **Bo** from the crew list in `variables.tf` and apply.

Read the plan before you say yes: only Bo's bunk may go. Ada's and Cyrus's bunks must **not** be rebuilt.

<br>

<details><summary>💡 Hint</summary>

Edit the default to `["Ada", "Cyrus"]`, then `terraform apply`. The plan should say `1 to destroy` and nothing else.

</details>

<details><summary>Solution</summary>

```plain
cd /root/bunks
sed -i 's/"Ada", "Bo", "Cyrus"/"Ada", "Cyrus"/' variables.tf
terraform apply -auto-approve
```{{exec}}

</details>
