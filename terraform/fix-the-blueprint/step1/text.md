In `/root/blueprint`, run `terraform validate` and read every error.
Fix the file until validate says **Success**.

⛔ Keep the `local_file` resource called `note` and keep its `lifecycle` settings: fix them, don't delete them.

<br>

<details><summary>💡 Hint</summary>

validate needs the provider schema first. Then: a nested block has **no equals sign**. And check the spelling of every argument name.

</details>

<details><summary>Solution</summary>

```plain
cd /root/blueprint
terraform init
sed -i 's/lifecycle = {/lifecycle {/; s/filname /filename/' main.tf
terraform fmt
terraform validate
```{{exec}}

</details>
