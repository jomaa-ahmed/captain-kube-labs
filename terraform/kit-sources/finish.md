# ⚒ Well built, Shipwright!

Registry modules use `NAMESPACE/NAME/PROVIDER` and a `version`; Git modules pin with `?ref=`. `terraform init`
downloads them into `.terraform/modules`, and `init -upgrade` moves to a newer allowed version, on purpose.
The lock file doesn't pin modules.

Next lab: **Terraform · Fleet kit** ⚒
