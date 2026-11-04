Add three outputs in `outputs.tf`, and apply:

| output | value |
|---|---|
| `names` | every ship name in capitals: `["KESTREL", "OSPREY", "WREN"]` |
| `files` | the `filename` of every `local_file.mast` |
| `big_ships` | the ships with **more than one** mast: `["kestrel", "osprey"]` |

⛔ `local_file.mast` was made with for_each: think before you reach for `[*]`.

<br>

<details><summary>💡 Hint</summary>

`[for name, m in var.masts : upper(name)]` · `[for f in local_file.mast : f.filename]` · `[for name, m in var.masts : name if m > 1]`. Splat only works on lists, sets and tuples; a for_each resource is a map.

</details>

<details><summary>Solution</summary>

```plain
cd /root/fleet
cat > outputs.tf <<'HCL'
output "names" {
  value = [for name, m in var.masts : upper(name)]
}

output "files" {
  value = [for f in local_file.mast : f.filename]
}

output "big_ships" {
  value = [for name, m in var.masts : name if m > 1]
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
