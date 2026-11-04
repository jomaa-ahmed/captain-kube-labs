The deck needs a note too: `deck.txt` saying `Teak, scrubbed daily`.

Put it in the crate **without editing `main.tf`**: set `notes` in a `terraform.tfvars` file (keep the three
other notes) and apply.

<br>

<details><summary>💡 Hint</summary>

terraform.tfvars is loaded automatically. Write the whole map: `notes = { "hull.txt" = "...", ..., "deck.txt" = "Teak, scrubbed daily" }` (copy the three values from variables.tf).

</details>

<details><summary>Solution</summary>

```plain
cd /root/crate
cat > terraform.tfvars <<'HCL'
notes = {
  "hull.txt" = "Oak, tarred twice"
  "mast.txt" = "Pine, 20 m"
  "sail.txt" = "Canvas, patched"
  "deck.txt" = "Teak, scrubbed daily"
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
