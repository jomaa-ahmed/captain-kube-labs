# Default cargo papers

Create a **LimitRange** **`defaults`** in namespace `shipyard` so every container that doesn't set its own gets:
* default **requests**: cpu **`100m`**, memory **`128Mi`**
* default **limits**: cpu **`500m`**, memory **`256Mi`**

<br>

<details><summary>💡 Hint</summary>

`kind: LimitRange`, `spec.limits[]` with `type: Container`, `defaultRequest:` (requests) and `default:` (limits).

</details>

<details><summary>Solution</summary>

```plain
cat > /root/defaults.yaml <<'EOF'
apiVersion: v1
kind: LimitRange
metadata:
  name: defaults
  namespace: shipyard
spec:
  limits:
  - type: Container
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 256Mi
EOF
kubectl apply -f /root/defaults.yaml
kubectl -n shipyard run test --image=nginx:1.27 --dry-run=server -o yaml | grep -A6 resources
```{{exec}}

</details>
