# Find what Helm created

One `helm install` created several Kubernetes objects at once.

Write the **name of the Deployment** that belongs to the release `web` into the file
**`/root/deployment.txt`** (just the name, nothing else).

<br>

<details><summary>💡 Hint</summary>

Helm labels everything it creates with `app.kubernetes.io/instance=<release>`.
Or ask Helm itself: `helm get manifest web -n docks`.

</details>

<details><summary>Solution</summary>

```plain
kubectl get deploy -n docks -l app.kubernetes.io/instance=web
```{{exec}}

```plain
kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}' > /root/deployment.txt
```{{exec}}

</details>
