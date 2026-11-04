Add a `check` block named `calm_seas` that **warns** when the log mentions `storm`, but never stops the run.

- `terraform plan -var 'weather=storm ahead'` must succeed **and** show `Check block assertion failed`
- `terraform plan` (calm weather) must show no warning

<br>

<details><summary>💡 Hint</summary>

`check "calm_seas" { assert { condition = !strcontains(local_file.log.content, "storm")  error_message = "..." } }`, at the top level, not inside the resource.

</details>

<details><summary>Solution</summary>

```plain
cd /root/lookout
cat >> main.tf <<'HCL'

check "calm_seas" {
  assert {
    condition     = !strcontains(local_file.log.content, "storm")
    error_message = "The log mentions a storm."
  }
}
HCL
terraform plan -var 'weather=storm ahead'
```{{exec}}

</details>
