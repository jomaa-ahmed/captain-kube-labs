In `/root/dock`, reach this state:
- `terraform init` and `terraform validate` succeed, apply works, and `terraform plan` says **No changes**
- `crew.txt` holds the same text as `orders.txt` (the data source stays)
- `env` only accepts `dev` or `prod`: `-var env=staging` stops the plan
- the hull is **replaced** whenever `var.recipe` changes
- a dock replacement (`-var build=v9`) **creates the new dock first**
- `terraform plan -destroy` stops with `Instance cannot be destroyed` (the ledger)

<br>

<details><summary>💡 Hint</summary>

Go error by error: init, validate, then plan. Look for: depends_on on an attribute, a variable in replace_triggered_by, a variable in lifecycle, a validation condition written backwards, and a seal nobody added.

</details>

<details><summary>Solution</summary>

```plain
cd /root/dock
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('depends_on = [local_file.orders.content]','depends_on = [local_file.orders]')
t=t.replace('replace_triggered_by = [var.recipe]','replace_triggered_by = [terraform_data.recipe]')
t=t.replace('create_before_destroy = var.safe','create_before_destroy = true')
t=t.replace('content  = "every ship we ever built"','content  = "every ship we ever built"\n\n  lifecycle {\n    prevent_destroy = true\n  }')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('!contains(["dev", "prod"], var.env)','contains(["dev", "prod"], var.env)')
open('variables.tf','w').write(v)
PY
terraform init
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
