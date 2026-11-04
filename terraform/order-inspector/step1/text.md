Add validation rules in `variables.tf`:
- `env` accepts only `dev` or `prod`
- `masts` accepts only 1 to 5

Each with a clear `error_message`. A bad value must stop `terraform plan` with `Invalid value for variable`;
`terraform plan -var env=prod -var masts=3` must still work.

<br>

<details><summary>💡 Hint</summary>

`validation { condition = contains(["dev", "prod"], var.env)  error_message = "..." }`. The condition is true for a GOOD value. For masts: `var.masts >= 1 && var.masts <= 5`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/inspect
cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env must be dev or prod."
  }
}

variable "masts" {
  type    = number
  default = 2

  validation {
    condition     = var.masts >= 1 && var.masts <= 5
    error_message = "A ship has 1 to 5 masts."
  }
}

variable "crew" {
  type    = list(string)
  default = ["Ada", "Bo"]
}
HCL
terraform plan -var env=staging || true
```{{exec}}

</details>
