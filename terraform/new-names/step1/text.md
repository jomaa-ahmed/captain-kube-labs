Rename `local_file.hull` to **`local_file.main_hull`** in the code, with a record that other environments
can apply too. Apply: the hull must not be rebuilt, and the plan must end with **No changes**.

<br>

<details><summary>💡 Hint</summary>

Rename the block, then add `moved { from = local_file.hull  to = local_file.main_hull }` and apply. `terraform state mv` would work here, but leaves no record in the code.

</details>

<details><summary>Solution</summary>

```plain
cd /root/names
sed -i 's/resource "local_file" "hull"/resource "local_file" "main_hull"/' main.tf
cat >> main.tf <<'HCL'

moved {
  from = local_file.hull
  to   = local_file.main_hull
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
