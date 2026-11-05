This time the change was **right**: the captain scrapped the mast on purpose, and `mast.txt` is gone.

Record that in the state **without rebuilding the mast**, then update the code so it agrees.
The plan must end with **No changes**, and `mast.txt` must not come back.

<br>

<details><summary>💡 Hint</summary>

`terraform plan -refresh-only` shows the change, `terraform apply -refresh-only` records it in the state only. Then delete the `local_file.mast` block from main.tf.

</details>

<details><summary>Solution</summary>

```plain
cd /root/pink
terraform plan -refresh-only
terraform apply -refresh-only -auto-approve
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'\nresource "local_file" "mast" \{.*?\n\}\n?', '\n', t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform plan
```{{exec}}

</details>
