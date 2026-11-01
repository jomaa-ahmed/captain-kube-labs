# Count the prod frontends

How many pods have **`env=prod`** **and** **`tier=frontend`**?
Write the number into **`/root/prod-frontend.txt`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl get pods -l key=value,key2=value2` (a comma means AND). `--show-labels` shows all labels.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods --show-labels
kubectl get pods -l env=prod,tier=frontend
```{{exec}}

```plain
kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l > /root/prod-frontend.txt
```{{exec}}

</details>
