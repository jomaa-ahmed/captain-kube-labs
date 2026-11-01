# The logbook is the truth

`kubectl get` just reads what etcd holds. Count the **Deployment keys** stored under
`/registry/deployments/kube-system` with etcdctl, and write the number into **`/root/deploy-count.txt`**.

Then compare with `kubectl get deploy -n kube-system`: same number?

<br>

<details><summary>💡 Hint</summary>

Same etcdctl command as before, with the prefix `/registry/deployments/kube-system` and `--keys-only`. Count the lines with `grep -c .`.

</details>

<details><summary>Solution</summary>

```plain
kubectl -n kube-system exec $(kubectl -n kube-system get pod -l component=etcd -o name) -- etcdctl \
  --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/deployments/kube-system --prefix --keys-only | grep -c . > /root/deploy-count.txt
```{{exec}}

```plain
cat /root/deploy-count.txt
kubectl get deploy -n kube-system
```{{exec}}

</details>
