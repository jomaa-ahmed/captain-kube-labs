In `main.tf`, write **one** resource `local_file.mast` with `for_each` over `var.masts`:

- file `<ship>.txt`, for example `osprey.txt`
- content `<ship>: <masts> masts`, for example `osprey: 3 masts`

Apply it. Adding a ship to the map later must need no new block.

<br>

<details><summary>💡 Hint</summary>

With a map, `each.key` is the ship and `each.value` the number: `filename = "${path.module}/${each.key}.txt"`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/fleet
cat > main.tf <<'HCL'
resource "local_file" "mast" {
  for_each = var.masts
  filename = "${path.module}/${each.key}.txt"
  content  = "${each.key}: ${each.value} masts"
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
