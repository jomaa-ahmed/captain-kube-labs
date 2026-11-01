# Render one template with a new value

The exam loves this one. Render **only the Deployment template**
(`templates/deployment.yaml`) with **4 replicas**, release name `preview`,
and save it to **`/root/deploy-4.yaml`**.

The file must contain only the Deployment, nothing else.

<br>

<details><summary>💡 Hint</summary>

`helm template` can show a single template (`--show-only`, short `-s`)
and accepts values with `--set key=value`.

</details>

<details><summary>Solution</summary>

```plain
helm template preview /root/charts/harbor-web -s templates/deployment.yaml --set replicaCount=4 > /root/deploy-4.yaml
```{{exec}}

```plain
grep -E '^kind|replicas' /root/deploy-4.yaml
```{{exec}}

</details>
