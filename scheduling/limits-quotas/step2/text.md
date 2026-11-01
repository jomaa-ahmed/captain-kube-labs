# Cap the shipyard

Create a **ResourceQuota** **`cap`** in namespace `shipyard` with:
* at most **5 pods**
* total **requests.cpu `1`**
* total **limits.memory `2Gi`**

<br>

<details><summary>💡 Hint</summary>

`kubectl create quota cap -n shipyard --hard=pods=5,requests.cpu=1,limits.memory=2Gi`

</details>

<details><summary>Solution</summary>

```plain
kubectl create quota cap -n shipyard --hard=pods=5,requests.cpu=1,limits.memory=2Gi
kubectl describe quota cap -n shipyard
```{{exec}}

</details>
