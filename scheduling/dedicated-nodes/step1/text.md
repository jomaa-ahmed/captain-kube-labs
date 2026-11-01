# Fence the dock

On **`node01`**:
1. add the taint **`team=gold:NoSchedule`**
2. add the label **`team=gold`**

<br>

<details><summary>💡 Hint</summary>

`kubectl taint nodes …` and `kubectl label nodes …` take the same `key=value` form.

</details>

<details><summary>Solution</summary>

```plain
kubectl taint nodes node01 team=gold:NoSchedule
kubectl label nodes node01 team=gold
```{{exec}}

</details>
