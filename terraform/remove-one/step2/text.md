The harbor master wants to **see** what a full teardown would do, before anyone decides.

Save a **destroy plan** to `/root/dismantle/teardown.tfplan`, and write in `/root/answers/destroy_count.txt`
how many resources it would destroy.

⛔ Don't destroy anything: the hull and the mast must still stand.

<br>

<details><summary>💡 Hint</summary>

`terraform plan -destroy -out=teardown.tfplan` shows the plan and saves it. Read the summary line.

</details>

<details><summary>Solution</summary>

```plain
cd /root/dismantle
terraform plan -destroy -out=teardown.tfplan
mkdir -p /root/answers
echo 2 > /root/answers/destroy_count.txt
```{{exec}}

</details>
