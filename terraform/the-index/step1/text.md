Write the value of the output `ship` into `/root/index/name.txt`, **without quotes**, using a terraform command
(no copy-paste, no editing the state).

<br>

<details><summary>💡 Hint</summary>

`terraform output ship` prints it with quotes; `terraform output -raw ship > name.txt` doesn't.

</details>

<details><summary>Solution</summary>

```plain
cd /root/index
terraform output -raw ship > name.txt
```{{exec}}

</details>
