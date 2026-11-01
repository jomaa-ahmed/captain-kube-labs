# The medic goes first

1. Create a PriorityClass **`critical-cargo`** with value **`1000000`** (not the global default)
2. Create a pod **`medic`** (image `nginx:1.27`) that uses it

<br>

<details><summary>💡 Hint</summary>

`kubectl create priorityclass critical-cargo --value=1000000`, then `priorityClassName:` in the pod spec.

</details>

<details><summary>Solution</summary>

```plain
kubectl create priorityclass critical-cargo --value=1000000 --description='medics first'
```{{exec}}

```plain
cat > /root/medic.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: medic
spec:
  priorityClassName: critical-cargo
  containers:
  - name: nginx
    image: nginx:1.27
EOF
kubectl apply -f /root/medic.yaml
```{{exec}}

</details>
