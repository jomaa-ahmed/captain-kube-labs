# Open it to the world

Create a Service **`web-public`** of type **NodePort** for the Deployment `web`,
on node port **30080**, so `curl http://localhost:30080` works from the node.

<br>

<details><summary>💡 Hint</summary>

`kubectl expose deployment web --name=web-public --type=NodePort --port=80` creates it with a random node port; set `nodePort: 30080` with `kubectl edit`, or write the YAML with `--dry-run=client -o yaml`.

</details>

<details><summary>Solution</summary>

```plain
kubectl expose deployment web --name=web-public --type=NodePort --port=80 --dry-run=client -o yaml > /root/web-public.yaml
```{{exec}}

```plain
sed -i 's/^  - port: 80$/  - port: 80\n    nodePort: 30080/' /root/web-public.yaml
kubectl apply -f /root/web-public.yaml
curl -s localhost:30080 | head -4
```{{exec}}

</details>
