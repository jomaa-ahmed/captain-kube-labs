# Write a pod in YAML

Write the file **`/root/lighthouse.yaml`** yourself and create the pod from it:

* name **`lighthouse`**, image **`nginx:1.27`**
* labels **`app=harbor`** and **`tier=front`**

The file must have the 4 top-level fields of every Kubernetes object.

<br>

<details><summary>💡 Hint</summary>

`apiVersion`, `kind`, `metadata` (name + labels), `spec` (containers: name + image). Then `kubectl apply -f /root/lighthouse.yaml`.

</details>

<details><summary>Solution</summary>

```plain
cat > /root/lighthouse.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: lighthouse
  labels:
    app: harbor
    tier: front
spec:
  containers:
  - name: nginx
    image: nginx:1.27
EOF
kubectl apply -f /root/lighthouse.yaml
```{{exec}}

</details>
