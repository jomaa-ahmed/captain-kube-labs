# ⚒ Well built, Shipwright!

default → `TF_VAR_flag` → terraform.tfvars → `*.auto.tfvars` (z beats a) → `-var` / `-var-file` in the order
typed. Other `.tfvars` files only load with `-var-file`: that's how one blueprint serves dev and prod.

Next lab: **Delivery receipt** ⚒
