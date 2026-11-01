# Launch the fleet

Create a Deployment **`cargo`** with image **`nginx:1.26`** and **3 replicas**.
Use one imperative command, as you would in the exam.

<br>

<details><summary>💡 Hint</summary>

`kubectl create deployment <name> --image=<image> --replicas=<n>`

</details>

<details><summary>Solution</summary>

```plain
kubectl create deployment cargo --image=nginx:1.26 --replicas=3
kubectl get deploy,rs,pods
```{{exec}}

</details>
