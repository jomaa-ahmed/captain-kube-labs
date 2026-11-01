# Declare the cargo

Create a pod **`crane`** (image `nginx:1.27`) with:
* requests: **cpu `100m`**, **memory `64Mi`**
* limits: **cpu `200m`**, **memory `128Mi`**

<br>

<details><summary>💡 Hint</summary>

Under the container: `resources: {requests: {cpu: …, memory: …}, limits: {…}}`. `kubectl explain pod.spec.containers.resources`.

</details>

<details><summary>Solution</summary>

```plain
cat > /root/crane.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: crane
spec:
  containers:
  - name: nginx
    image: nginx:1.27
    resources:
      requests:
        cpu: 100m
        memory: 64Mi
      limits:
        cpu: 200m
        memory: 128Mi
EOF
kubectl apply -f /root/crane.yaml
```{{exec}}

</details>
