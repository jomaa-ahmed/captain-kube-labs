Each mast needs at least one crew member. Add a **precondition** to `local_file.ship` so that a plan with more
masts than crew stops with `Resource precondition failed`.

With the default crew (Ada, Bo): `-var masts=2` plans fine, `-var masts=3` must fail.

<br>

<details><summary>💡 Hint</summary>

Inside the resource: `lifecycle { precondition { condition = length(var.crew) >= var.masts  error_message = "..." } }`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/inspect
sed -i 's|  content  = "${var.env}: ${var.masts} masts, ${length(var.crew)} crew"|&\n\n  lifecycle {\n    precondition {\n      condition     = length(var.crew) >= var.masts\n      error_message = "Each mast needs at least one crew member."\n    }\n  }|' main.tf
terraform plan -var masts=3 || true
```{{exec}}

</details>
