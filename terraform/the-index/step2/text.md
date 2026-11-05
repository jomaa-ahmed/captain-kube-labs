What `file_permission` does `local_file.hull` have in the state? Write the value alone into `/root/index/perm.txt`.

<br>

<details><summary>💡 Hint</summary>

`terraform state show local_file.hull` lists every attribute of that one resource.

</details>

<details><summary>Solution</summary>

```plain
cd /root/index
terraform state show -no-color local_file.hull
terraform show -json | $PY -c "import json,sys; print([r['values']['file_permission'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='local_file.hull'][0])" > perm.txt
```{{exec}}

</details>
