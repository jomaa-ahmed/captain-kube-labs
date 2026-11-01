# Rescue the ferry 🔧

The pod **`ferry`** can't start. Find out why and fix it, so `ferry` is **Running**
with the **Alpine** variant of nginx 1.27. Keep the name `ferry`.

<br>

<details><summary>💡 Hint</summary>

`kubectl get pod ferry` shows the status, `kubectl describe pod ferry` shows the events at the bottom. A pod's image can be changed in place: `kubectl set image` or `kubectl edit`.

</details>

<details><summary>Solution</summary>

```plain
kubectl describe pod ferry | tail -5
```{{exec}}

```plain
kubectl set image pod/ferry ferry=nginx:1.27-alpine
kubectl get pod ferry -w
```{{exec}}

</details>
