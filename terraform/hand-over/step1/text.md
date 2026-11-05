Make Terraform **stop managing** `local_file.logbook` without deleting `logbook.txt`, with a plan you can review.
Remove its resource block. Plan: **No changes** at the end, and `logbook.txt` still there.

<br>

<details><summary>💡 Hint</summary>

Replace the resource block with `removed { from = local_file.logbook  lifecycle { destroy = false } }`, then `terraform apply`. Just deleting the block would destroy the file.

</details>

<details><summary>Solution</summary>

```plain
cd /root/handover
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'resource "local_file" "logbook" \{.*?\n\}', 'removed {\n  from = local_file.logbook\n\n  lifecycle {\n    destroy = false\n  }\n}', t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve
```{{exec}}

</details>
