# A watchtower on node01

Create a **static pod** **`watchtower`** (image `nginx:1.27`) on **`node01`**.
The kubelet on node01 must start it from a file, not the API.

You can reach node01 with `ssh node01`.

<br>

<details><summary>💡 Hint</summary>

Generate the YAML with `kubectl run watchtower --image=nginx:1.27 --dry-run=client -o yaml`, then on node01 put it in the kubelet's `staticPodPath` (see `/var/lib/kubelet/config.yaml`). The API shows it as `watchtower-node01`.

</details>

<details><summary>Solution</summary>

```plain
kubectl run watchtower --image=nginx:1.27 --dry-run=client -o yaml > /root/watchtower.yaml
scp /root/watchtower.yaml node01:/etc/kubernetes/manifests/
kubectl get pods -o wide | grep watchtower
```{{exec}}

</details>
