A harbor script needs the ship's name in `/root/receipt/name.txt`: **just the name**,
no quotes. Get it from `terraform output`.

<br>

<details><summary>💡 Hint</summary>

`terraform output ship_name` prints it in quotes. `-raw` prints the plain string, ready for scripts.

</details>

<details><summary>Solution</summary>

```plain
cd /root/receipt
terraform output -raw ship_name > name.txt
```{{exec}}

</details>
