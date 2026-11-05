1. Move `label` to exactly **`0.25.0`** (plan first: what does Terraform say?), and install it.
2. Add a second copy from **Git**: module **`label_git`** with source
   `git::https://github.com/cloudposse/terraform-null-label.git`, pinned to the tag `0.25.0`,
   `namespace = "sy"`, `stage = "dev"`, `name = "kestrel"`, and a root output **`dev_id`**.

Apply. `terraform output -raw dev_id` must print `sy-dev-kestrel`.

<br>

<details><summary>💡 Hint</summary>

After changing `version`, `terraform init -upgrade` installs it. Git modules have no version argument: add `?ref=0.25.0` to the source URL.

</details>

<details><summary>Solution</summary>

```plain
cd /root/sources
sed -i 's/version   = "0.24.1"/version   = "0.25.0"/' main.tf
cat >> main.tf <<'HCL'

module "label_git" {
  source    = "git::https://github.com/cloudposse/terraform-null-label.git?ref=0.25.0"
  namespace = "sy"
  stage     = "dev"
  name      = "kestrel"
}

output "dev_id" {
  value = module.label_git.id
}
HCL
terraform init -upgrade
terraform apply -auto-approve
```{{exec}}

</details>
