# Too big for any dock 🔧

The pod **`giant`** has been `Pending` since you arrived. Find out why and get it running.
It must still **request** CPU (don't just delete the requests): **`250m`** is plenty.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe pod giant` → Events: "Insufficient cpu". Compare its request with `kubectl describe node | grep -A5 Allocatable`.

</details>

<details><summary>Solution</summary>

```plain
kubectl describe pod giant | tail -3
kubectl get pod giant -o yaml > /root/giant.yaml
```{{exec}}

```plain
sed -i 's/cpu: "64"/cpu: 250m/' /root/giant.yaml
kubectl replace --force -f /root/giant.yaml
kubectl get pod giant
```{{exec}}

</details>
