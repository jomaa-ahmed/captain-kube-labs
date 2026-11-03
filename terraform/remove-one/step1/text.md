Remove **only** the old boat: `old_boat.txt` must disappear and leave the state.

⛔ `hull`, `mast` and `neighbor.txt` must stay.

<br>

<details><summary>💡 Hint</summary>

Delete the old boat's block from `main.tf`, then apply: the plan says *will be destroyed, because it's not in configuration*.

</details>

<details><summary>Solution</summary>

```plain
cd /root/dismantle
$PY - <<'PY'
import re
p='main.tf'; t=open(p).read()
t=re.sub(r'resource "local_file" "old_boat" \{.*?\n\}\n?', '', t, flags=re.S)
open(p,'w').write(t)
PY
terraform apply -auto-approve
```{{exec}}

</details>
