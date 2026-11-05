Add a root output **`kestrel_file`** that returns the module's `file` output, and apply.
`terraform output -raw kestrel_file` must print `./dock-kestrel.txt`.

<br>

<details><summary>💡 Hint</summary>

Module results are `module.LABEL.OUTPUT`: `output "kestrel_file" { value = module.kestrel.file }`. The resources inside the module aren't reachable from the root.

</details>

<details><summary>Solution</summary>

```plain
cd /root/kit
cat >> main.tf <<'HCL'

output "kestrel_file" {
  value = module.kestrel.file
}
HCL
terraform apply -auto-approve
terraform output -raw kestrel_file
```{{exec}}

</details>
