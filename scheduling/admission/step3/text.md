# See it work

Without creating any namespace yourself, run a pod **`sentry`** (image `nginx:1.27`) in the namespace
**`frontier`**, which doesn't exist yet.

<br>

<details><summary>💡 Hint</summary>

`kubectl run … -n frontier`. Normally this fails with "namespaces not found": the new plugin creates it on the fly.

</details>

<details><summary>Solution</summary>

```plain
kubectl get ns frontier
kubectl run sentry --image=nginx:1.27 -n frontier
kubectl get ns frontier
```{{exec}}

</details>
