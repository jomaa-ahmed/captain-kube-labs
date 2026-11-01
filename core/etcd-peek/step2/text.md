# Find the lighthouse

The etcd image contains `etcdctl`. Run it **inside the etcd pod** with the certificates, list the keys
under `/registry/pods/default`, and write the **key of pod `lighthouse`** into **`/root/lighthouse-key.txt`**.

<br>

<details><summary>💡 Hint</summary>

`kubectl exec -n kube-system <etcd-pod> -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=… --cert=… --key=… get /registry/pods/default --prefix --keys-only`. The server cert and key sit next to the CA file.

</details>

<details><summary>Solution</summary>

```plain
kubectl -n kube-system exec $(kubectl -n kube-system get pod -l component=etcd -o name) -- etcdctl \
  --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/pods/default --prefix --keys-only
```{{exec}}

```plain
echo /registry/pods/default/lighthouse > /root/lighthouse-key.txt
```{{exec}}

</details>
