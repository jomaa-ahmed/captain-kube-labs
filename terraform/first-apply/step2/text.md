Someone deleted `hello.txt` by hand. 🌊

Run a **plan** first and read it: what does Terraform want to do, and why?
Then bring the file back **the Terraform way**, so the plan ends with *No changes*.

⛔ Writing the file by hand doesn't count: the ledger (state) must record the rebuild.

<br>

<details><summary>💡 Hint</summary>

`terraform plan` shows `+ create`: the blueprint and the ledger say *a file*, the real world says *nothing*. Apply it.

</details>

<details><summary>Solution</summary>

```plain
cd /root/shipyard
terraform plan
terraform apply -auto-approve
```{{exec}}

</details>
