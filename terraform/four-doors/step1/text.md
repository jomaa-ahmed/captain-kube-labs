Make `terraform validate` succeed and apply. The goal: `orders.txt` says `build 3 masts`, and both
`crew.txt` and `log.txt` copy the **orders**.

<br>

<details><summary>💡 Hint</summary>

Validate shows a typo (Did you mean \"filename\"?) and an `Error: Cycle`: crew reads the log and the log reads the crew. Point both at `local_file.orders.content`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/doors
sed -i 's/filname/filename/' main.tf
sed -i 's/local_file.log.content/local_file.orders.content/; s/local_file.crew.content/local_file.orders.content/' main.tf
terraform validate
terraform apply -auto-approve
```{{exec}}

</details>
