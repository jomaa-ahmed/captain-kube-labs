A good kit rejects bad orders. Add a **validation** to the module's `masts` variable: 1 to 5.

`terraform plan -var 'fleet={"kestrel"=9}'` must fail with `Invalid value for variable`, and the normal plan
must still say **No changes**.

<br>

<details><summary>💡 Hint</summary>

Inside `variable "masts"` in modules/mast/variables.tf: `validation { condition = var.masts >= 1 && var.masts <= 5  error_message = "A ship has 1 to 5 masts." }`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/fleet
$PY - <<'PY'
t=open('modules/mast/variables.tf').read()
t=t.replace('description = "Number of masts"','description = "Number of masts"\n\n  validation {\n    condition     = var.masts >= 1 && var.masts <= 5\n    error_message = "A ship has 1 to 5 masts."\n  }')
open('modules/mast/variables.tf','w').write(t)
PY
terraform plan -var 'fleet={"kestrel"=9}' || true
```{{exec}}

</details>
