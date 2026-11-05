In `/root/stray`, adopt the code `Kestrel42` as **`random_string.code`**:

- write an `import` block, and let Terraform write the resource block (`-generate-config-out=generated.tf`)
- clean the generated file: no `= null` lines left
- apply. `random_string.code` must have the result `Kestrel42`, and the plan must end with **No changes**

<br>

<details><summary>💡 Hint</summary>

`import { to = random_string.code  id = "Kestrel42" }` in import.tf, then `terraform plan -generate-config-out=generated.tf`, `sed -i '/= null/d' generated.tf`, `terraform apply`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/stray
cat > import.tf <<'HCL'
import {
  to = random_string.code
  id = "Kestrel42"
}
HCL
terraform plan -generate-config-out=generated.tf
sed -i '/= null/d' generated.tf
terraform apply -auto-approve
```{{exec}}

</details>
