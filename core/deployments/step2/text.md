# Roll out a new version

Update `cargo` to **`nginx:1.27`** and watch the rollout replace the pods one by one.

⚠️ Update the Deployment you have: don't delete it.

<br>

<details><summary>💡 Hint</summary>

`kubectl set image deployment/<name> <container>=<image>`. The container is called `nginx`. Watch with `kubectl rollout status`.

</details>

<details><summary>Solution</summary>

```plain
kubectl set image deployment/cargo nginx=nginx:1.27
kubectl rollout status deployment/cargo
kubectl get rs
```{{exec}}

</details>
