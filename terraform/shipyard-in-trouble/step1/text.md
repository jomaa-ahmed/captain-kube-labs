In `/root/boss`, reach this state:
- `terraform fmt -check` passes and `terraform validate` says Success
- the local provider is on the **2.4.x** line that `main.tf` asks for
- `cargo.txt` says exactly **`Ship: <the pet's id>`**
- `terraform plan` says **No changes**

⛔ The ship (`random_pet.ship`) is already built: keep the same pet. ⛔ No hand edits of the lock file.

<br>

<details><summary>💡 Hint</summary>

Go fault by fault: init (read the error), validate (read the errors), plan (read every symbol). One file went missing by hand...

</details>

<details><summary>Solution</summary>

```plain
cd /root/boss
terraform init -upgrade
sed -i 's/lifecycle = {/lifecycle {/' main.tf
terraform fmt
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
