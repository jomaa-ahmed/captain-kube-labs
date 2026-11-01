# Watch the control loop

Delete **one** pod of the ReplicaSet `crew` and watch what happens.

Write the name of the **new pod** the ReplicaSet created into **`/root/new-pod.txt`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl get pods -l app=crew`, delete one with `kubectl delete pod <name>`, then list again: the youngest pod (smallest AGE) is the new one.

</details>

<details><summary>Solution</summary>

```plain
kubectl delete pod $(kubectl get pods -l app=crew -o jsonpath='{.items[0].metadata.name}')
```{{exec}}

```plain
kubectl get pods -l app=crew --sort-by=.metadata.creationTimestamp
kubectl get pods -l app=crew --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}' > /root/new-pod.txt
```{{exec}}

</details>
