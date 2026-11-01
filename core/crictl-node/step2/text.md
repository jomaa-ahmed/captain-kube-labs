# Find the container

Use `crictl` to find the **container ID** of the nginx container in pod `lighthouse`.
Write it into **`/root/container-id.txt`** (the short 13-character ID is fine).

<br>

<details><summary>💡 Hint</summary>

`crictl ps` lists containers with their pod name. `crictl ps --name nginx` or `--pod <pod-id>` filters.

</details>

<details><summary>Solution</summary>

```plain
crictl pods --name lighthouse
crictl ps --name lighthouse
```{{exec}}

```plain
crictl ps --name lighthouse -q | head -1 > /root/container-id.txt
```{{exec}}

</details>
