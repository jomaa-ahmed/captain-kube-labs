# The storm 🌪️

`NoSchedule` only stops **new** pods. Look: `drifter` still runs on node01 without any toleration.

Add a second taint to node01: key **`storm`**, value **`true`**, effect **`NoExecute`**,
and watch what happens to the pods on node01.

<br>

<details><summary>💡 Hint</summary>

Same `kubectl taint` command, different effect. Then `kubectl get pods -o wide -w`.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods -o wide
kubectl taint nodes node01 storm=true:NoExecute
kubectl get pods -o wide -w
```{{exec}}

</details>
