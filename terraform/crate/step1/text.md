Replace the literal `source` blocks with **one** `dynamic "source"` block over `var.notes`, so the crate holds
**every** note (`hull.txt`, `mast.txt`, `sail.txt`). Apply and check: `unzip -l crate.zip`.

<br>

<details><summary>💡 Hint</summary>

`dynamic "source" { for_each = var.notes  content { filename = source.key  content = source.value } }`. Inside, the item is named after the block label, not `each`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/crate
cat > main.tf <<'HCL'
data "archive_file" "crate" {
  type        = "zip"
  output_path = "${path.module}/crate.zip"

  dynamic "source" {
    for_each = var.notes
    content {
      filename = source.key
      content  = source.value
    }
  }
}

output "crate_size" {
  value = data.archive_file.crate.output_size
}
HCL
terraform apply -auto-approve
unzip -l crate.zip || true
```{{exec}}

</details>
