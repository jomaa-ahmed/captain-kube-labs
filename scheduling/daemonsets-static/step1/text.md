# A lamp on every dock

Create a **DaemonSet** **`lamp`** (image `busybox:1.36`, command `sleep 1d`) that runs **one pod on every node**,
**including the controlplane**.

<br>

<details><summary>💡 Hint</summary>

Start from a Deployment YAML (`kubectl create deployment lamp --image=busybox:1.36 --dry-run=client -o yaml`), change `kind` to DaemonSet and remove `replicas` and `strategy`. Does the controlplane have a taint?

</details>

<details><summary>Solution</summary>

```plain
kubectl describe node controlplane | grep -i taints
```{{exec}}

```plain
cat > /root/lamp.yaml <<'EOF'
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lamp
spec:
  selector:
    matchLabels: {app: lamp}
  template:
    metadata:
      labels: {app: lamp}
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      containers:
      - name: lamp
        image: busybox:1.36
        command: ["sleep", "1d"]
EOF
kubectl apply -f /root/lamp.yaml
kubectl get pods -l app=lamp -o wide
```{{exec}}

</details>
