# Find the one that is not a pod

One node component can't be a pod: it's the captain who starts all the pods.

1. Write its **name** into **`/root/not-a-pod.txt`**
2. Write the path of **its config file** into **`/root/kubelet-config.txt`**

<br>

<details><summary>💡 Hint</summary>

It runs as a normal Linux service. `systemctl status <name>` and `ps aux | grep <name>` show how it was started, including a `--config=` flag.

</details>

<details><summary>Solution</summary>

```plain
systemctl status kubelet --no-pager | head -5
ps aux | grep -o -- '--config=[^ ]*'
```{{exec}}

```plain
echo kubelet > /root/not-a-pod.txt
echo /var/lib/kubelet/config.yaml > /root/kubelet-config.txt
```{{exec}}

</details>
