# Set-based selectors

Find the pods whose **`env` is `prod` or `staging`**, but whose **team is not `red`**.
Write their **names**, one per line, into **`/root/selected.txt`**.

<br>

<details><summary>💡 Hint</summary>

Set-based syntax: `-l 'env in (prod,staging),team!=red'`. `-o name` or `-o custom-columns=:metadata.name` prints names.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods -l 'env in (prod,staging),team!=red' -o custom-columns=:metadata.name --no-headers > /root/selected.txt
cat /root/selected.txt
```{{exec}}

</details>
