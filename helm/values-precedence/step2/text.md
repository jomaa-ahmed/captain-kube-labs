# Upgrade without losing settings

It's a quiet day. Scale the shop down to **1 replica** with **`helm upgrade`**.

⚠️ The trap: after the upgrade the service must **still be `NodePort`** and the pods must
**still have the label `team=harbor`**. An upgrade doesn't remember your old `--set` and `-f` by itself.

<br>

<details><summary>💡 Hint</summary>

Either pass the file and all the settings again, or tell Helm to reuse the last release's values
and change only one: `--reuse-values`.

</details>

<details><summary>Solution</summary>

```plain
helm upgrade shop /root/charts/harbor-web -n market --reuse-values --set replicaCount=1
```{{exec}}

```plain
helm history shop -n market
kubectl get deploy,svc -n market
```{{exec}}

</details>
