# Waiting for a ghost pilot 🔧

The pod **`parcel`** has been `Pending` forever, with no events at all. Find out why and get it running
with the cluster's **default scheduler**.

<br>

<details><summary>💡 Hint</summary>

`kubectl get pod parcel -o yaml | grep -i scheduler`. Is there a scheduler with that name in kube-system? The field can't be changed on a running pod: recreate it.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pod parcel -o jsonpath='{.spec.schedulerName}'; echo
kubectl get pods -n kube-system | grep scheduler
```{{exec}}

```plain
kubectl get pod parcel -o yaml > /root/parcel.yaml
sed -i 's/schedulerName: night-pilot/schedulerName: default-scheduler/' /root/parcel.yaml
kubectl replace --force -f /root/parcel.yaml
kubectl get pod parcel
```{{exec}}

</details>
