# Ask for a LoadBalancer

In the cloud, a **LoadBalancer** Service gets a public IP from the cloud provider. This harbor has no cloud.

1. Create a Service **`web-lb`** of type **LoadBalancer** for the Deployment `web`, on port **80**
2. Look at its **EXTERNAL-IP** column and write exactly what you see there into **`/root/lb-external.txt`**
3. A LoadBalancer is built **on top of a NodePort**: write its node port into **`/root/lb-nodeport.txt`**
   and check that `curl http://localhost:<that port>` already works

<br>

<details><summary>💡 Hint</summary>

`kubectl expose deployment web --name=web-lb --type=LoadBalancer --port=80`, then `kubectl get svc web-lb`. The node port is in the PORT(S) column (`80:3xxxx/TCP`) or `-o jsonpath='{.spec.ports[0].nodePort}'`.

</details>

<details><summary>Solution</summary>

```plain
kubectl expose deployment web --name=web-lb --type=LoadBalancer --port=80
kubectl get svc web-lb
```{{exec}}

```plain
echo '<pending>' > /root/lb-external.txt
kubectl get svc web-lb -o jsonpath='{.spec.ports[0].nodePort}' > /root/lb-nodeport.txt
curl -s localhost:$(cat /root/lb-nodeport.txt) | head -4
```{{exec}}

</details>
