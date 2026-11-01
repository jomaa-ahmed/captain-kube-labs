# Move into the market

You'll work in `market` a lot. Make **`market`** the **default namespace** of your current context,
so `kubectl get pods` shows the market without `-n`.

<br>

<details><summary>💡 Hint</summary>

`kubectl config set-context --current --namespace=<ns>`

</details>

<details><summary>Solution</summary>

```plain
kubectl config set-context --current --namespace=market
kubectl get pods
```{{exec}}

</details>
