# Hire more crew

Big cargo today. Scale the ReplicaSet **`crew`** to **5** pods, all ready.

<br>

<details><summary>💡 Hint</summary>

`kubectl scale rs <name> --replicas=N`, or change `replicas` with `kubectl edit rs crew`.

</details>

<details><summary>Solution</summary>

```plain
kubectl scale rs crew --replicas=5
kubectl get rs crew
```{{exec}}

</details>
