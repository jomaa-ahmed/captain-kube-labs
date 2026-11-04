Run `terraform plan` in `/root/register` and look at what it would do to `ships.txt`. 😱

Fix the blueprint so that `banner.txt` holds the register **in capitals**, by **reading** `ships.txt`.

⛔ `ships.txt` must not change, and must not be managed by Terraform (no `local_file.register` in the state).

<br>

<details><summary>💡 Hint</summary>

Replace the `resource "local_file" "register"` block with `data "local_file" "register" { filename = ... }` (no content), and reference it as `data.local_file.register.content`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/register
$PY - <<'PY'
import re
p='main.tf'; t=open(p).read()
t=re.sub(r'resource "local_file" "register" \{.*?\n\}', 'data "local_file" "register" {\n  filename = "${path.module}/ships.txt"\n}', t, flags=re.S)
t=t.replace('local_file.register.content', 'data.local_file.register.content')
open(p,'w').write(t)
PY
terraform apply -auto-approve
```{{exec}}

</details>
