The crew now wants a container image, managed with the **Docker** provider (written by the company
*kreuzwerker*, not by HashiCorp). See `docker.tf`. `terraform init` fails.

Read the error, then make `terraform init` and `terraform validate` succeed.
The lock file must record `kreuzwerker/docker`.

⛔ Don't apply: there's no Docker engine in this harbor. `validate` is enough.

<br>

<details><summary>💡 Hint</summary>

Without a `source`, Terraform guesses `hashicorp/docker`, which doesn't exist. Add a `terraform { required_providers { docker = { source = "kreuzwerker/docker" } } }` block.

</details>

<details><summary>Solution</summary>

```plain
cd /root/supplier
terraform init || true
cat > versions.tf <<'HCL'
terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}
HCL
terraform init
terraform validate
```{{exec}}

</details>
