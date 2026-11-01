# East or west

1. Label **`node01`** with **`zone=east`**
2. Create a Deployment **`analytics`** (image `nginx:1.27`, **2 replicas**) whose pods **must** run on nodes where
   **`zone` is `east` or `west`**, using **required node affinity** with the `In` operator.

<br>

<details><summary>💡 Hint</summary>

`spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[].matchExpressions[]` with `key: zone`, `operator: In`, `values: [east, west]`. `kubectl explain deployment.spec.template.spec.affinity.nodeAffinity` helps.

</details>

<details><summary>Solution</summary>

```plain
kubectl label nodes node01 zone=east
```{{exec}}

```plain
cat > /root/analytics.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics
spec:
  replicas: 2
  selector:
    matchLabels: {app: analytics}
  template:
    metadata:
      labels: {app: analytics}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values: [east, west]
      containers:
      - name: nginx
        image: nginx:1.27
EOF
kubectl apply -f /root/analytics.yaml
```{{exec}}

</details>
