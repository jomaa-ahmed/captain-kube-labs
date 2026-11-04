Add a `locals` block with `prefix = "shipyard-${var.env}"`, and use `local.prefix` everywhere instead.

This is a **refactor**: nothing real may change. After your edit, `terraform plan` must say **No changes**.

<br>

<details><summary>💡 Hint</summary>

`locals { prefix = "shipyard-${var.env}" }` (block: locals, plural) and `"${local.prefix}-hull.txt"` (reference: local, singular).

</details>

<details><summary>Solution</summary>

```plain
cd /root/margin
$PY - <<'PY'
p='main.tf'; t=open(p).read()
t=t.replace('shipyard-${var.env}', '${local.prefix}')
t='locals {\n  prefix = "shipyard-${var.env}"\n}\n\n'+t
open(p,'w').write(t)
PY
terraform plan
```{{exec}}

</details>
