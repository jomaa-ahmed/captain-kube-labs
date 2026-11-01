# The fast lane

1. Label **`node01`** with **`disk=ssd`**
2. Create a pod **`fastlane`** (image `nginx:1.27`) that may only run on nodes with **`disk=ssd`**, using a **nodeSelector**

<br>

<details><summary>💡 Hint</summary>

`kubectl label nodes node01 disk=ssd`. In the pod: `spec.nodeSelector: {disk: ssd}`.

</details>

<details><summary>Solution</summary>

```plain
kubectl label nodes node01 disk=ssd
```{{exec}}

```plain
cat > /root/fastlane.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: fastlane
spec:
  nodeSelector:
    disk: ssd
  containers:
  - name: nginx
    image: nginx:1.27
EOF
kubectl apply -f /root/fastlane.yaml
```{{exec}}

</details>
