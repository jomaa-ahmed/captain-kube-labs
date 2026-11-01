# Find the keys to the logbook

etcd only talks to clients with the right certificates. Its static pod manifest says which files it uses.

Write the path of etcd's **trusted CA file** into **`/root/etcd-ca.txt`**.

<br>

<details><summary>💡 Hint</summary>

Look in `/etc/kubernetes/manifests/etcd.yaml` for a flag with `trusted-ca` in its name.

</details>

<details><summary>Solution</summary>

```plain
grep -E 'crt|key' /etc/kubernetes/manifests/etcd.yaml
```{{exec}}

```plain
grep -o -- '--trusted-ca-file=[^ ]*' /etc/kubernetes/manifests/etcd.yaml | cut -d= -f2 > /root/etcd-ca.txt
```{{exec}}

</details>
