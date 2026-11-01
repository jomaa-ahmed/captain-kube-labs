# Find the static pods

Nobody created the control-plane pods with `kubectl`: the **kubelet** starts them from YAML files in a folder
on the node. These are **static pods**.

1. Write the **folder path** into **`/root/manifests.txt`**
2. Write **how many manifest files** are in it into **`/root/manifests-count.txt`**

<br>

<details><summary>💡 Hint</summary>

The kubelet's config file says where it looks: search it for `staticPodPath`. The config file is `/var/lib/kubelet/config.yaml`.

</details>

<details><summary>Solution</summary>

```plain
grep staticPodPath /var/lib/kubelet/config.yaml
```{{exec}}

```plain
ls /etc/kubernetes/manifests
echo /etc/kubernetes/manifests > /root/manifests.txt
ls /etc/kubernetes/manifests | wc -l > /root/manifests-count.txt
```{{exec}}

</details>
