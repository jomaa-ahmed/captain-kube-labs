In `/root/yard`, reach this state:
- `terraform validate` says Success and `terraform plan` says **No changes**
- one bunk per crew member, **keyed by name** (`local_file.bunk["Ada"]`...), each file saying `Bunk of <name>`
- `manifest.txt` says exactly `PROD-KESTREL: 3 masts, flag violet`
- the same blueprint in dev (`-var env=dev`) would give `DEV-KESTREL`, **1** mast and flag **grey**
- `crate.zip` holds every note in `var.notes`
- `terraform output bunks` lists every bunk's filename

⛔ When someone leaves the crew later, only their bunk may be destroyed.

<br>

<details><summary>💡 Hint</summary>

Go error by error: validate, then plan. Look for: a list given to for_each, a conditional whose two sides have different types, a function that doesn't exist, the wrong item name inside a dynamic block, and a splat on a for_each resource.

</details>

<details><summary>Solution</summary>

```plain
cd /root/yard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('for_each = var.crew','for_each = toset(var.crew)')
t=t.replace('["violet"]','"violet"')
t=t.replace('shipname(var.env, var.ship)','upper("${var.env}-${var.ship}")')
t=t.replace('filename = each.key\n      content  = each.value','filename = source.key\n      content  = source.value')
open('main.tf','w').write(t)
o=open('outputs.tf').read().replace('local_file.bunk[*].filename','[for b in local_file.bunk : b.filename]')
open('outputs.tf','w').write(o)
PY
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
