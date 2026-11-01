# Who's at the gate?

Find the value of the API server flag **`--enable-admission-plugins`** and write it
(just the value, e.g. `A,B`) into **`/root/plugins.txt`**.

<br>

<details><summary>💡 Hint</summary>

The flag is in `/etc/kubernetes/manifests/kube-apiserver.yaml`.

</details>

<details><summary>Solution</summary>

```plain
grep enable-admission /etc/kubernetes/manifests/kube-apiserver.yaml
```{{exec}}

```plain
grep -o -- '--enable-admission-plugins=[^ ]*' /etc/kubernetes/manifests/kube-apiserver.yaml | cut -d= -f2 > /root/plugins.txt
```{{exec}}

</details>
