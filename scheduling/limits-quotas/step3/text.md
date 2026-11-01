# The welders are short-handed 🔧

The Deployment **`welders`** in `shipyard` wants **6** pods, but fewer are running. Find out why.

The harbor master agrees to allow **8 pods** in the shipyard. Change the quota so all 6 welders run.

⚠️ Keep the quota and its CPU and memory caps: only raise the pod count.

<br>

<details><summary>💡 Hint</summary>

Pods that a quota refuses never appear: look at the ReplicaSet's events, `kubectl -n shipyard describe rs -l app=welders`. Then `kubectl -n shipyard edit quota cap`.

</details>

<details><summary>Solution</summary>

```plain
kubectl -n shipyard get deploy welders
kubectl -n shipyard describe rs -l app=welders | grep -i quota | tail -2
```{{exec}}

```plain
kubectl -n shipyard patch quota cap -p '{"spec":{"hard":{"pods":"8"}}}'
kubectl -n shipyard get deploy welders -w
```{{exec}}

</details>
