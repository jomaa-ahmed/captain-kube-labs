# Render without installing

Render the chart with the release name **`preview`** and save the YAML to
**`/root/rendered.yaml`**.

⚠️ Nothing may be installed in the cluster: no release, no new objects.

<br>

<details><summary>💡 Hint</summary>

There is a Helm command that only **renders** templates to YAML and never talks to the cluster.
It takes the same release name and chart as `helm install`.

</details>

<details><summary>Solution</summary>

```plain
helm template preview /root/charts/harbor-web > /root/rendered.yaml
```{{exec}}

```plain
grep '^kind:' /root/rendered.yaml
```{{exec}}

</details>
