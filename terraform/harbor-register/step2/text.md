Every ship needs a captain. Add to `main.tf`:
- a `random_pet` called `captain`
- a `local_file` called `captain` that writes `captain.txt` with exactly **`Captain: <the pet's id>`**

**Before** you apply, run `terraform plan` and write in `/root/answers/known.txt` the name of the
`random_pet.captain` attribute that shows **(known after apply)**. Then apply.

<br>

<details><summary>💡 Hint</summary>

Reference it as `random_pet.captain.id`. In the plan, `length` and `separator` are known, the id isn't yet.

</details>

<details><summary>Solution</summary>

```plain
cd /root/register
cat >> main.tf <<'HCL'

resource "random_pet" "captain" {}

resource "local_file" "captain" {
  filename = "${path.module}/captain.txt"
  content  = "Captain: ${random_pet.captain.id}"
}
HCL
terraform init
terraform plan
mkdir -p /root/answers
echo id > /root/answers/known.txt
terraform apply -auto-approve
```{{exec}}

</details>
