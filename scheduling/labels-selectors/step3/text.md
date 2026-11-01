# The Service catches too much 🔧

The Service **`radar`** should only send traffic to **prod frontend** pods.
Right now it also sends traffic to dev and staging pods. Fix it.

⚠️ Fix the Service you have: don't delete it, and don't change the pods' labels.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe svc radar` shows its selector and endpoints. A selector with two labels matches only pods that have **both**. `kubectl edit svc radar` or `kubectl set selector svc radar …`.

</details>

<details><summary>Solution</summary>

```plain
kubectl describe svc radar
```{{exec}}

```plain
kubectl set selector svc radar env=prod,tier=frontend
kubectl describe svc radar | grep -i endpoints
```{{exec}}

</details>
