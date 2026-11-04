Switch the bunks from `count` to **for_each**, so each bunk is keyed by its crew member's name:

- addresses `local_file.bunk["Ada"]`, `["Bo"]`, `["Cyrus"]`
- file `bunk-<name>.txt` containing `Bunk of <name>`

Apply it. Moving from count to for_each rebuilds the bunks once; that's fine here (Module 9 shows `moved`).

<br>

<details><summary>💡 Hint</summary>

for_each takes a map or a set of strings, and `var.crew` is a list: `for_each = toset(var.crew)`. Inside, use `each.key` (or `each.value`, the same for a set).

</details>

<details><summary>Solution</summary>

```plain
cd /root/bunks
cat > main.tf <<'HCL'
resource "local_file" "bunk" {
  for_each = toset(var.crew)
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.value}"
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
