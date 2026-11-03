Add a second `local` provider configuration with **alias `backup`**, and a new resource
`local_file` called `backup` that writes `backup.txt` (any content) **through that alias**. Apply.

<br>

<details><summary>💡 Hint</summary>

`provider "local" { alias = "backup" }`, then in the resource: `provider = local.backup` (no quotes).

</details>

<details><summary>Solution</summary>

```plain
cd /root/harbors
cat >> main.tf <<'HCL'

provider "local" {
  alias = "backup"
}

resource "local_file" "backup" {
  provider = local.backup
  filename = "${path.module}/backup.txt"
  content  = "backup records"
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
