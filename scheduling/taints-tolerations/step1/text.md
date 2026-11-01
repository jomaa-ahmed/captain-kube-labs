# Raise the hazard flag

Taint **`node01`** with key **`cargo`**, value **`hazardous`** and effect **`NoSchedule`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl taint nodes <node> key=value:Effect`

</details>

<details><summary>Solution</summary>

```plain
kubectl taint nodes node01 cargo=hazardous:NoSchedule
kubectl describe node node01 | grep -i taints
```{{exec}}

</details>
