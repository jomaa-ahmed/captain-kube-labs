# Call the pilot back

Someone moved the scheduler's static pod manifest out of the manifests folder.
Find it somewhere under `/etc/kubernetes` and **put it back**, so the scheduler pod runs again.

<br>

<details><summary>💡 Hint</summary>

`find /etc/kubernetes -name '*scheduler*'`. The kubelet starts static pods from `/etc/kubernetes/manifests`.

</details>

<details><summary>Solution</summary>

```plain
find /etc/kubernetes -name '*scheduler*.yaml'
```{{exec}}

```plain
mv /etc/kubernetes/parked/kube-scheduler.yaml /etc/kubernetes/manifests/
kubectl get pods -n kube-system -l component=kube-scheduler -w
```{{exec}}

</details>
