Run `terraform plan` in `/root/plan` and write your answers in `/root/answers/`:
- `replaced.txt`: the address of the resource that will be **replaced** (-/+)
- `destroyed.txt`: the address of the resource that will be **destroyed** only (-)
- `add.txt`: the number in the summary line after **to add**

<br>

<details><summary>💡 Hint</summary>

Look for `must be replaced` and `will be destroyed`. A replacement also counts in *to add*.

</details>

<details><summary>Solution</summary>

```plain
cd /root/plan
terraform plan
mkdir -p /root/answers
echo local_file.replace_me > /root/answers/replaced.txt
echo local_file.delete_me > /root/answers/destroyed.txt
echo 2 > /root/answers/add.txt
```{{exec}}

</details>
