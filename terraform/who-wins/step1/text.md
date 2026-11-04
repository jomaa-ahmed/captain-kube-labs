Without changing anything: which value does `var.flag` get when you run a plain `terraform plan`?
Write it in `/root/answers/winner.txt`.

You may check yourself with `echo var.flag | terraform console`.

<br>

<details><summary>💡 Hint</summary>

Later sources win: default → environment → terraform.tfvars → *.auto.tfvars (alphabetical) → -var / -var-file. Which files load on their own?

</details>

<details><summary>Solution</summary>

```plain
cd /root/wins
echo var.flag | terraform console
mkdir -p /root/answers
echo z-auto > /root/answers/winner.txt
```{{exec}}

</details>
