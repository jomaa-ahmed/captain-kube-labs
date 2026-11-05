Switch `local_file.bunk` from `count` to **`for_each = toset(var.crew)`**, keyed by name
(`bunk["Ada"]`, `bunk["Bo"]`). Same files, nothing rebuilt, plan: **No changes**.

<br>

<details><summary>💡 Hint</summary>

Keep the filename `bunk-<name>.txt` and the content. Add one moved block per bunk: `from = local_file.bunk[0]  to = local_file.bunk["Ada"]`, and [1] → ["Bo"].

</details>

<details><summary>Solution</summary>

```plain
cd /root/names
$PY - <<'PY'
import re
t=open('main.tf').read()
new='''resource "local_file" "bunk" {
  for_each = toset(var.crew)
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.key}"
}

moved {
  from = local_file.bunk[0]
  to   = local_file.bunk["Ada"]
}

moved {
  from = local_file.bunk[1]
  to   = local_file.bunk["Bo"]
}'''
t=re.sub(r'resource "local_file" "bunk" \{.*?\n\}', new, t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve
```{{exec}}

</details>
