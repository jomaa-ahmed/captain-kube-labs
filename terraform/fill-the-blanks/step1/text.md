In `/root/blanks`:
1. Declare a variable `ship_name` in `variables.tf`, with `type = string`, a `description`, and **no default**
2. Use it in both files instead of `Kestrel`
3. Put `ship_name = "Osprey"` in `terraform.tfvars`, then apply

`hull.txt` must say `Hull of the Osprey`, `flag.txt` must say `Flag of the Osprey`.

<br>

<details><summary>💡 Hint</summary>

`variable "ship_name" { type = string  description = "..." }` and `"Hull of the ${var.ship_name}"`. terraform.tfvars is loaded automatically.

</details>

<details><summary>Solution</summary>

```plain
cd /root/blanks
cat > variables.tf <<'HCL'
variable "ship_name" {
  type        = string
  description = "Name of the ship on the order"
}
HCL
sed -i 's/Kestrel/${var.ship_name}/' main.tf
echo 'ship_name = "Osprey"' > terraform.tfvars
terraform apply -auto-approve
```{{exec}}

</details>
