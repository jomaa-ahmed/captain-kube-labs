# Read Chart.yaml and values.yaml

Answer two questions about the chart at `/root/charts/harbor-web`:

1. Write the chart's **version** into **`/root/chart-version.txt`**
2. Write the default **replicaCount** into **`/root/replicas.txt`**

<br>

<details><summary>💡 Hint</summary>

The chart's identity card is `Chart.yaml`. The defaults live in `values.yaml`.
Helm can show both: `helm show chart <chart>` and `helm show values <chart>`.

</details>

<details><summary>Solution</summary>

```plain
helm show chart /root/charts/harbor-web | grep '^version'
```{{exec}}

```plain
helm show values /root/charts/harbor-web | grep replicaCount
```{{exec}}

```plain
echo 0.1.0 > /root/chart-version.txt
echo 2 > /root/replicas.txt
```{{exec}}

</details>
