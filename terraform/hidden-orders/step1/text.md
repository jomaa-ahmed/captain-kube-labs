Tell Terraform that `data.local_file.orders` must wait for `local_file.orders`, then apply.

`crew.txt` must say `build 3 masts`.

<br>

<details><summary>💡 Hint</summary>

Inside the data block: `depends_on = [local_file.orders]`. A whole resource, not one of its attributes.

</details>

<details><summary>Solution</summary>

```plain
cd /root/orders
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('data "local_file" "orders" {\n  filename = "${path.module}/orders.txt"', 'data "local_file" "orders" {\n  filename   = "${path.module}/orders.txt"\n  depends_on = [local_file.orders]')
open('main.tf','w').write(t)
PY
terraform apply -auto-approve
```{{exec}}

</details>
