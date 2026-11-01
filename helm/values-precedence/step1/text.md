# Install with a file and --set

Install `/root/charts/harbor-web` as release **`shop`** in namespace **`market`** (create it), using:

* the values file **`/root/prod-values.yaml`**
* and on the command line: **3 replicas** and service type **`NodePort`**

Use Helm for every setting: no `kubectl edit` or `kubectl scale` afterwards.

<br>

<details><summary>💡 Hint</summary>

`-f <file>` for the file, `--set key=value` for the rest. Several values: `--set a=1,b=2`.
Look at `values.yaml` to find the key for the service type.

</details>

<details><summary>Solution</summary>

```plain
helm install shop /root/charts/harbor-web -n market --create-namespace \
  -f /root/prod-values.yaml --set replicaCount=3,service.type=NodePort
```{{exec}}

```plain
kubectl get deploy,svc -n market
```{{exec}}

</details>
