# An address for the backend

The pod **`client`** needs to reach the Deployment **`api`** at **`http://api`**.
Create a **ClusterIP** Service called **`api`** on port **80** for it.

Test: `kubectl exec client -- wget -qO- -T 3 http://api`

<br>

<details><summary>💡 Hint</summary>

`kubectl expose deployment api --port=80` creates a ClusterIP Service named after the Deployment.

</details>

<details><summary>Solution</summary>

```plain
kubectl expose deployment api --port=80
kubectl exec client -- wget -qO- -T 3 http://api | head -4
```{{exec}}

</details>
