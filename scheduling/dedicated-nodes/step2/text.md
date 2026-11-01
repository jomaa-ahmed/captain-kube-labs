# Team gold sails in

Create a Deployment **`gold-app`** (image `nginx:1.27`, **3 replicas**) whose pods:
* **tolerate** the taint `team=gold:NoSchedule`
* **must** run on nodes labelled `team=gold` (required node affinity)

All 3 pods must land on node01.

<br>

<details><summary>💡 Hint</summary>

Under `spec.template.spec` you need both `tolerations:` and `affinity.nodeAffinity.requiredDuring…`.

</details>

<details><summary>Solution</summary>

```plain
cat > /root/gold-app.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gold-app
spec:
  replicas: 3
  selector:
    matchLabels: {app: gold-app}
  template:
    metadata:
      labels: {app: gold-app}
    spec:
      tolerations:
      - key: team
        operator: Equal
        value: gold
        effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: team
                operator: In
                values: [gold]
      containers:
      - name: nginx
        image: nginx:1.27
EOF
kubectl apply -f /root/gold-app.yaml
kubectl get pods -l app=gold-app -o wide
```{{exec}}

</details>
