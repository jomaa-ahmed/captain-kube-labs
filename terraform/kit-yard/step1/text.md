In `/root/kityard`, reach this state:
- `terraform init` and `terraform validate` succeed, and `terraform plan` says **No changes**
- `dock-kestrel.txt` says `kestrel: 3 masts`
- `terraform output -raw dock_file` prints `./dock-kestrel.txt`
- `terraform output -raw label_id` prints `sy-prod-kestrel`, from `cloudposse/label/null` pinned to exactly **0.25.0**

<br>

<details><summary>💡 Hint</summary>

Look for: a variable in a module source, a version on a local module, a missing required input, and an output that reaches inside a module.

</details>

<details><summary>Solution</summary>

```plain
cd /root/kityard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('source  = var.label_source','source  = "cloudposse/label/null"')
t=t.replace('  version = "1.0.0"\n','')
t=t.replace('  masts  = 3','  name   = "kestrel"\n  masts  = 3')
t=t.replace('module.dock.local_file.this.filename','module.dock.file')
open('main.tf','w').write(t)
PY
terraform init
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
