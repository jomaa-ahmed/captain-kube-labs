# Fix the deckhands 🔧

The ReplicaSet **`deckhands`** has pods that never start. Fix it so **both** pods run **`nginx:1.27`**.

⚠️ Don't delete or recreate the ReplicaSet itself: fix the one you have.

<br>

<details><summary>💡 Hint</summary>

Fixing the image in the ReplicaSet template is only half the job: a ReplicaSet doesn't replace pods that already exist. What happens if the old pods go away?

</details>

<details><summary>Solution</summary>

```plain
kubectl describe pods -l app=deckhands | grep -A3 Events
```{{exec}}

```plain
kubectl set image rs/deckhands nginx=nginx:1.27
kubectl delete pods -l app=deckhands
kubectl get pods -l app=deckhands
```{{exec}}

</details>
