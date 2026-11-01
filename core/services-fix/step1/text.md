# Fix the web Service 🔧

The Service **`web`** has an address, but nothing answers. Fix it so
`curl http://<web ClusterIP>` returns the nginx welcome page.

⚠️ Fix the Service you have: don't delete it or create a new one.
There may be more than one thing wrong.

<br>

<details><summary>💡 Hint</summary>

Compare the Service's **selector** with the pod labels (`kubectl get pods --show-labels`), and its **targetPort** with the port nginx listens on. `kubectl get endpointslices -l kubernetes.io/service-name=web` shows whether it found pods.

</details>

<details><summary>Solution</summary>

```plain
kubectl describe svc web
kubectl get pods --show-labels
```{{exec}}

```plain
kubectl patch svc web -p '{"spec":{"selector":{"app":"web"},"ports":[{"port":80,"targetPort":80}]}}'
```{{exec}}

```plain
curl -s http://$(kubectl get svc web -o jsonpath='{.spec.clusterIP}') | head -4
```{{exec}}

</details>
