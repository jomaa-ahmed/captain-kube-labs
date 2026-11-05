Someone added `local_file.hull`. Validate passes, but `terraform apply` fails. Read the error: which door is it?

The folder `hull.txt/` is an old leftover nobody needs. Fix it so `hull.txt` is a file saying `oak`,
and the plan ends with **No changes**. The resource keeps its filename.

<br>

<details><summary>💡 Hint</summary>

`Error: Create local file error ... is a directory` comes from the provider: the real world is in the way. Remove the folder (`rm -rf hull.txt`) and apply again.

</details>

<details><summary>Solution</summary>

```plain
cd /root/doors
terraform apply -auto-approve || true
rm -rf hull.txt
terraform apply -auto-approve
```{{exec}}

</details>
