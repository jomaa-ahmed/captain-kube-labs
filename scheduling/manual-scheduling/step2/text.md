# Pilot it yourself

No scheduler? Then you are the pilot. Get the pod **`cargo`** (image `nginx:1.27`) **running on `node01`**,
without bringing the scheduler back yet.

<br>

<details><summary>💡 Hint</summary>

A pod's `spec.nodeName` skips the scheduler completely, but it can only be set when the pod is created. Delete `cargo` and create it again with `nodeName: node01`.

</details>

<details><summary>Solution</summary>

```plain
kubectl delete pod cargo --now
kubectl run cargo --image=nginx:1.27 --overrides='{"spec":{"nodeName":"node01"}}'
kubectl get pod cargo -o wide
```{{exec}}

</details>
