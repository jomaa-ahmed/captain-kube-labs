# Find the pod's address

Every pod gets its own IP from its **sandbox**. Use `crictl inspectp` on the lighthouse pod sandbox
and write the pod's **IP address** into **`/root/pod-ip.txt`**.

<br>

<details><summary>💡 Hint</summary>

`crictl pods --name lighthouse -q` gives the sandbox ID; `crictl inspectp <id> | grep -i ip`.

</details>

<details><summary>Solution</summary>

```plain
crictl inspectp $(crictl pods --name lighthouse -q) | grep '"ip"'
```{{exec}}

```plain
crictl inspectp $(crictl pods --name lighthouse -q) | grep -m1 '"ip"' | grep -oE '[0-9.]{7,}' > /root/pod-ip.txt
```{{exec}}

</details>
