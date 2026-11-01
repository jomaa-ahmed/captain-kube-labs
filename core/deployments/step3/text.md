# Undo the bad rollout 🔧

Oh no: a crew member just pushed a new version of `cargo`, and the new pods won't start. 🌊
(Look: `kubectl get pods`.)

Find it in the rollout history and **undo** it, so all 3 pods run `nginx:1.27` again.

⚠️ Use the rollout history: no new `set image`, no delete and recreate.

<br>

<details><summary>💡 Hint</summary>

`kubectl rollout history deployment/cargo` lists the revisions. `kubectl rollout undo` goes back one revision (or `--to-revision=N`).

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods
kubectl rollout history deployment/cargo
```{{exec}}

```plain
kubectl rollout undo deployment/cargo
kubectl rollout status deployment/cargo
```{{exec}}

</details>
