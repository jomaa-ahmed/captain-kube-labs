# A tanker with papers

Create a pod **`tanker`** (image `nginx:1.27`) that **tolerates** the taint and **runs on `node01`**.

Remember: the toleration alone doesn't send it to node01. Use `nodeSelector` with the label
`kubernetes.io/hostname: node01` to pin it.

<br>

<details><summary>💡 Hint</summary>

Generate a pod with `kubectl run tanker --image=nginx:1.27 --dry-run=client -o yaml`, then add `tolerations:` (key, operator Equal, value, effect) and `nodeSelector:` under `spec`.

</details>

<details><summary>Solution</summary>

```plain
cat > /root/tanker.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: tanker
spec:
  nodeSelector:
    kubernetes.io/hostname: node01
  tolerations:
  - key: cargo
    operator: Equal
    value: hazardous
    effect: NoSchedule
  containers:
  - name: nginx
    image: nginx:1.27
EOF
kubectl apply -f /root/tanker.yaml
kubectl get pod tanker -o wide
```{{exec}}

</details>
