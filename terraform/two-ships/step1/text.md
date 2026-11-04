Change `local.masts` so it is **3 in prod** and **1 everywhere else**, then build prod:

```
terraform apply -var env=prod
```

`ship.txt` must say `Kestrel (prod) masts: 3`, and the same blueprint must still give 1 mast in dev.

💡 Try your expression first in `terraform console`.

<br>

<details><summary>💡 Hint</summary>

condition ? value_if_true : value_if_false. Compare with `==`: `var.env == "prod" ? 3 : 1`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/two
sed -i 's/masts = 1/masts = var.env == "prod" ? 3 : 1/' main.tf
terraform apply -var env=prod -auto-approve
```{{exec}}

</details>
