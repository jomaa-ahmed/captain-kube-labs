# Install the release

Install the chart at `/root/charts/harbor-web` as a release named **`web`**
in the namespace **`docks`**. The namespace doesn't exist yet.

When you're done, the release must be `deployed` and its pod must be running.

<br>

<details><summary>💡 Hint</summary>

`helm install <release> <chart> -n <namespace>` · there's a flag that creates the namespace for you:

```plain
helm install --help | grep namespace
```{{exec}}

</details>

<details><summary>Solution</summary>

```plain
helm install web /root/charts/harbor-web -n docks --create-namespace
```{{exec}}

```plain
helm list -n docks
kubectl get pods -n docks
```{{exec}}

</details>
