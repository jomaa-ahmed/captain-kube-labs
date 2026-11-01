# Why is the cargo waiting?

The pod **`cargo`** is stuck in `Pending`. Look at the control plane and find which component is missing.

Write its name into **`/root/missing.txt`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe pod cargo` shows no scheduling events at all. Compare `kubectl get pods -n kube-system` with the four control-plane components.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pod cargo
kubectl get pods -n kube-system
```{{exec}}

```plain
echo kube-scheduler > /root/missing.txt
```{{exec}}

</details>
