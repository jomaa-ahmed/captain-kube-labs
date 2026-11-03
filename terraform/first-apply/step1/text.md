Go to `/root/shipyard`, prepare the folder and build the blueprint.

When you're done, `hello.txt` must exist and the state must list `local_file.hello`.

<br>

<details><summary>💡 Hint</summary>

Two commands: one prepares the folder (downloads the provider), one builds. Add `-auto-approve` or type `yes`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/shipyard
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
