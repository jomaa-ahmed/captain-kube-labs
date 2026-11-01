# The barge can't moor 🔧

A new pod **`barge`** just arrived for node01 and is stuck in `Pending`.
Find out why and get it **running on node01**.

⚠️ Keep node01's taint as it is: fix the barge.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe pod barge` → Events say which taint it doesn't tolerate. Compare its toleration with the taint, letter by letter. Tolerations of an existing pod can't be changed: export it, fix it, recreate it.

</details>

<details><summary>Solution</summary>

```plain
kubectl describe pod barge | tail -4
kubectl get pod barge -o yaml > /root/barge.yaml
```{{exec}}

```plain
sed -i 's/value: hazardus/value: hazardous/' /root/barge.yaml
kubectl replace --force -f /root/barge.yaml
kubectl get pod barge -o wide
```{{exec}}

</details>
