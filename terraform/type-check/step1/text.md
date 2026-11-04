`keel.txt` must hold the **first** wood of `woods`, in the order it's written (`oak`), and the list must keep
every entry, duplicates included. Run `terraform plan`, read the error, fix the blueprint, apply.

⛔ Keep reading the value from `var.woods` (no hard-coded `"oak"`).

<br>

<details><summary>💡 Hint</summary>

`Elements of a set are identified only by their value and don't have any separate index or key`. A **list** keeps order and duplicates: `type = list(string)`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/types
terraform plan || true
sed -i 's/type    = set(string)/type    = list(string)/' variables.tf
terraform apply -auto-approve
```{{exec}}

</details>
