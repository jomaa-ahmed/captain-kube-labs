It works, but HashiCorp calls `depends_on` a last resort. Here a plain reference says the same thing.

Remove the data source and the `depends_on`, and let `local_file.crew` read **`local_file.orders.content`** directly.
Apply: `crew.txt` is unchanged, and the plan ends with **No changes**.

<br>

<details><summary>💡 Hint</summary>

A reference is an implicit dependency: `content = local_file.orders.content`. Then delete the whole `data "local_file" "orders"` block.

</details>

<details><summary>Solution</summary>

```plain
cd /root/orders
cat > main.tf <<'HCL'
resource "local_file" "orders" {
  filename = "${path.module}/orders.txt"
  content  = "build 3 masts"
}

resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = local_file.orders.content
}
HCL
terraform apply -auto-approve
```{{exec}}

</details>
