# Bring the harbor back 🔥

Goal: from the node,
`curl http://<harbor-web ClusterIP>` returns the nginx welcome page, served by **2 healthy pods**.

Faults hidden here: **3**.

<br>

<details><summary>💡 Hint</summary>

Work from the inside out: are the pods running (`kubectl -n harbor get pods`, `describe`)? Does the Service find them (`kubectl -n harbor get endpointslices`)? Does it send traffic to the right port (`kubectl -n harbor describe svc harbor-web`)?

</details>

<details><summary>Solution</summary>

```plain
kubectl -n harbor get pods
kubectl -n harbor describe pod -l app=harbor-web | grep -A2 -i failed
```{{exec}}

```plain
kubectl -n harbor set image deploy/harbor-web nginx=nginx:1.27-alpine
kubectl -n harbor rollout status deploy/harbor-web
```{{exec}}

```plain
kubectl -n harbor patch svc harbor-web -p '{"spec":{"selector":{"app":"harbor-web"},"ports":[{"port":80,"targetPort":80}]}}'
```{{exec}}

```plain
curl -s http://$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.clusterIP}') | head -4
```{{exec}}

</details>
