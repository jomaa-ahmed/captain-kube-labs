# Read the ranks

Kubernetes ships with built-in PriorityClasses. Write the **value** of **`system-node-critical`**
into **`/root/node-critical.txt`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl get priorityclass`

</details>

<details><summary>Solution</summary>

```plain
kubectl get priorityclass
kubectl get pc system-node-critical -o jsonpath='{.value}' > /root/node-critical.txt
```{{exec}}

</details>
