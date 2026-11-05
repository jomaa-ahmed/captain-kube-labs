A second code exists: `Osprey7`. Adopt it as **`random_string.osprey`**, this time with the
**`terraform import`** command. It needs the resource block first (`length = 7`).

The plan must end with **No changes**.

<br>

<details><summary>💡 Hint</summary>

Write `resource "random_string" "osprey" { length = 7 }`, then `terraform import random_string.osprey Osprey7`. One resource per command, and no plan before it.

</details>

<details><summary>Solution</summary>

```plain
cd /root/stray
cat > osprey.tf <<'HCL'
resource "random_string" "osprey" {
  length = 7
}
HCL
terraform import random_string.osprey Osprey7
terraform plan
```{{exec}}

</details>
