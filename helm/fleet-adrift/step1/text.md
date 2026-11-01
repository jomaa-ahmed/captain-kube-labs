# Find the logbook & clear the ghost 🔥

1. Helm stores its release history inside Kubernetes **Secrets** in the release's namespace (`armada`).
   Inspect them and write their Secret **`TYPE`** into **`/root/secret-type.txt`**.
2. Uninstall the release **`ghost`** from **`armada`** cleanly with Helm, so both its objects and its release Secrets are gone.

<br>

<details><summary>💡 Hint</summary>

`kubectl get secrets -n armada` shows the release Secrets and their `TYPE` column. `helm uninstall <release> -n <ns>` removes a release and its history.

</details>

<details><summary>Solution</summary>

```plain
kubectl get secrets -n armada
kubectl get secrets -n armada -l owner=helm -o jsonpath='{.items[0].type}' > /root/secret-type.txt
cat /root/secret-type.txt
```{{exec}}

```plain
helm uninstall ghost -n armada
helm list -n armada
```{{exec}}

</details>
