The root needs the file's **content**. Add an output `content` in the module, and a root output
**`kestrel_content`** that returns it. `terraform output -raw kestrel_content` must print `prod: kestrel`.

<br>

<details><summary>💡 Hint</summary>

Module: `output "content" { value = local_file.this.content }`. Root: `output "kestrel_content" { value = module.kestrel.content }`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/sealed
printf '\noutput "content" {\n  value = local_file.this.content\n}\n' >> modules/dock/outputs.tf
printf '\noutput "kestrel_content" {\n  value = module.kestrel.content\n}\n' >> main.tf
terraform apply -auto-approve
```{{exec}}

</details>
