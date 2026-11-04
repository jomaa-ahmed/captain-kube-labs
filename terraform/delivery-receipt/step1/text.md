Read the error from `terraform plan`, then fix `outputs.tf`:
- `dock_code` stays an output, but must never print on the screen
- add an output `ship_name` with the pet's id

Apply. `terraform output` must show `dock_code = <sensitive>` and the ship's name.

<br>

<details><summary>💡 Hint</summary>

`Output refers to sensitive values`: random_password's result is sensitive. Add `sensitive = true` to the dock_code output.

</details>

<details><summary>Solution</summary>

```plain
cd /root/receipt
cat > outputs.tf <<'HCL'
output "dock_code" {
  value     = random_password.dock_code.result
  sensitive = true
}

output "ship_name" {
  value = random_pet.ship.id
}
HCL
terraform apply -auto-approve
terraform output
```{{exec}}

</details>
