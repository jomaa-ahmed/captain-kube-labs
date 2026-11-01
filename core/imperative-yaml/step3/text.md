# Apply it

Now create the beacon **declaratively** from your file, so later changes to the file can be applied again.

<br>

<details><summary>💡 Hint</summary>

`kubectl apply -f` remembers what you applied (in an annotation); `kubectl create -f` doesn't.

</details>

<details><summary>Solution</summary>

```plain
kubectl apply -f /root/beacon.yaml
kubectl get deploy beacon -o yaml | grep -A1 last-applied | head -3
```{{exec}}

</details>
