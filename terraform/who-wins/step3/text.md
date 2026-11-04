Last question, no apply needed. What does `var.flag` become with:

```
terraform plan -var 'flag=cli' -var-file=prod.tfvars
```

Write the value in `/root/answers/order.txt`.

<br>

<details><summary>💡 Hint</summary>

On the command line, flags are read in the order you type them: the last one wins.

</details>

<details><summary>Solution</summary>

```plain
mkdir -p /root/answers
echo prod > /root/answers/order.txt
```{{exec}}

</details>
