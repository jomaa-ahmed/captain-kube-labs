# Generate, don't type

Write the YAML for a Deployment **`beacon`** (image **`nginx:1.27`**, **2 replicas**) into
**`/root/beacon.yaml`**, using kubectl to generate it.

⚠️ Don't create the Deployment yet: only the file.

<br>

<details><summary>💡 Hint</summary>

`kubectl create deployment … --dry-run=client -o yaml > file` prints the object instead of creating it.

</details>

<details><summary>Solution</summary>

```plain
kubectl create deployment beacon --image=nginx:1.27 --replicas=2 --dry-run=client -o yaml > /root/beacon.yaml
cat /root/beacon.yaml
```{{exec}}

</details>
