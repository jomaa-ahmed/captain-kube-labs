In `/root/order`, reach this state:
- `terraform validate` says Success and `terraform plan` says **No changes**
- `crew.txt` is **read**, never managed or changed (it's the harbor master's list)
- `manifest.txt` says exactly:
  ```
  prod-Kestrel: 2 masts, flag violet
  crew: <the content of crew.txt>
  ```
- `terraform output -raw label` prints `prod-Kestrel`
- `dock_code` is an output that never shows on the screen

⛔ Customers don't always say the flag: it must default to **violet**.

<br>

<details><summary>💡 Hint</summary>

Go error by error: validate, then plan. Look for: a resource that should be a data source, a reference with the wrong prefix, a value of the wrong type, an object attribute that should be optional, a sensitive output.

</details>

<details><summary>Solution</summary>

```plain
cd /root/order
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'resource "local_file" "crew" \{.*?\n\}', 'data "local_file" "crew" {\n  filename = "${path.module}/crew.txt"\n}', t, flags=re.S)
t=t.replace('local_file.crew.content','data.local_file.crew.content').replace('locals.label','local.label')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('flag = string','flag = optional(string, "violet")')
open('variables.tf','w').write(v)
o=open('terraform.tfvars').read().replace('masts = "two"','masts = 2')
open('terraform.tfvars','w').write(o)
out=open('outputs.tf').read().replace('value = random_password.dock_code.result','value     = random_password.dock_code.result\n  sensitive = true')
open('outputs.tf','w').write(out)
PY
terraform fmt
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
