# Add a sidecar

Create a pod **`signal`** with **two containers**:

* **`web`**: image `nginx:1.27`
* **`logger`**: image `busybox:1.36`, command `sh -c 'while true; do echo ahoy; sleep 5; done'`

Both containers must be ready, and `logger` must be printing `ahoy`.

<br>

<details><summary>💡 Hint</summary>

Start from `kubectl run signal --image=nginx:1.27 --dry-run=client -o yaml > signal.yaml`, rename the container to `web` and add a second item under `containers`.

</details>

<details><summary>Solution</summary>

```plain
cat > /root/signal.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: signal
spec:
  containers:
  - name: web
    image: nginx:1.27
  - name: logger
    image: busybox:1.36
    command: ["sh", "-c", "while true; do echo ahoy; sleep 5; done"]
EOF
kubectl apply -f /root/signal.yaml
kubectl logs signal -c logger
```{{exec}}

</details>
