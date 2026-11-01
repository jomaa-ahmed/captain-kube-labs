# Name the runtime

Write the **name of the container runtime** this node uses into **`/root/runtime.txt`**
(just the name, no version).

<br>

<details><summary>💡 Hint</summary>

`crictl version` prints `RuntimeName`. `kubectl get nodes -o wide` shows it too.

</details>

<details><summary>Solution</summary>

```plain
crictl version
```{{exec}}

```plain
crictl version | awk '/RuntimeName/{print $2}' > /root/runtime.txt
```{{exec}}

</details>
