# The reports never sail 🔧

The Deployment **`reports`** should run on the **large** node (node01), but its pods stay `Pending`.
Fix the Deployment so both pods run on node01.

⚠️ Don't change the node labels: fix the Deployment.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe pod -l app=reports` → "didn't match Pod's node affinity". Compare the affinity (`kubectl get deploy reports -o yaml`) with `kubectl get node node01 --show-labels`. Labels are case-sensitive.

</details>

<details><summary>Solution</summary>

```plain
kubectl get node node01 --show-labels | tr ',' '\n' | grep size
kubectl get deploy reports -o yaml | grep -A3 'key: size'
```{{exec}}

```plain
kubectl patch deploy reports --type=json -p='[{"op":"replace","path":"/spec/template/spec/affinity/nodeAffinity/requiredDuringSchedulingIgnoredDuringExecution/nodeSelectorTerms/0/matchExpressions/0/values","value":["large"]}]'
kubectl get pods -l app=reports -o wide
```{{exec}}

</details>
