# Open a new gate

Enable the admission plugin **`NamespaceAutoProvision`** (keep the plugins that are already there).

After you save the manifest, the kubelet restarts the API server: `kubectl` won't answer for up to a minute.
Wait until `kubectl get nodes` works again.

<br>

<details><summary>💡 Hint</summary>

Add `,NamespaceAutoProvision` to the end of the `--enable-admission-plugins=` value. Back up first: `cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.bak` (never inside the manifests folder).

</details>

<details><summary>Solution</summary>

```plain
cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.bak
sed -i 's/--enable-admission-plugins=\(.*\)$/--enable-admission-plugins=\1,NamespaceAutoProvision/' /etc/kubernetes/manifests/kube-apiserver.yaml
grep enable-admission /etc/kubernetes/manifests/kube-apiserver.yaml
```{{exec}}

```plain
watch -n 3 kubectl get nodes
```{{exec}}

</details>
