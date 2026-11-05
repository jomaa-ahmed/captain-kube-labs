In `/root/audit`, reach this state:
- `terraform validate` succeeds and `terraform plan` says **No changes**
- the hull is managed as **`local_file.main_hull`**, and `hull.txt` was **not rebuilt**
- the logbook is **no longer managed** by Terraform, and `logbook.txt` still exists
- the dock code `Kestrel42` (made by hand) is managed as **`random_string.code`** with that exact value

<br>

<details><summary>💡 Hint</summary>

Validate first (a typo). Then: a moved block for the rename, a removed block (destroy = false) for the logbook, an import block (plus a resource block with length = 9, or generated config) for the code.

</details>

<details><summary>Solution</summary>

```plain
cd /root/audit
sed -i 's/contnet/content/' main.tf
cat >> main.tf <<'HCL'

moved {
  from = local_file.hull
  to   = local_file.main_hull
}

removed {
  from = local_file.logbook

  lifecycle {
    destroy = false
  }
}

import {
  to = random_string.code
  id = "Kestrel42"
}

resource "random_string" "code" {
  length = 9
}
HCL
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
