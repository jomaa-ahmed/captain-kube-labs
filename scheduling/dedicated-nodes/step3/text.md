# The batch job strays 🔧

Team gold just deployed **`gold-batch`**. Look where its pods landed: `kubectl get pods -l app=gold-batch -o wide`.

Some of them moor at the controlplane, outside the gold dock. Fix `gold-batch` so **all** its pods run on node01.

<br>

<details><summary>💡 Hint</summary>

It has the papers (toleration) but nothing sends it to node01. Add the same required node affinity as gold-app.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods -l app=gold-batch -o wide
```{{exec}}

```plain
kubectl patch deploy gold-batch -p '{"spec":{"template":{"spec":{"affinity":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"team","operator":"In","values":["gold"]}]}]}}}}}}}'
kubectl rollout status deploy/gold-batch
kubectl get pods -l app=gold-batch -o wide
```{{exec}}

</details>
