# Find the harbor office

The control plane runs as pods in the namespace `kube-system`.

1. Write the name of the **etcd pod** into **`/root/etcd-pod.txt`**
2. Write the name of the **node** where the **kube-apiserver** pod runs into **`/root/api-node.txt`**

<br>

<details><summary>💡 Hint</summary>

`kubectl get pods -n kube-system -o wide` shows every pod with its node.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods -n kube-system -o wide
```{{exec}}

```plain
kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}' > /root/etcd-pod.txt
kubectl get pods -n kube-system -l component=kube-apiserver -o jsonpath='{.items[0].spec.nodeName}' > /root/api-node.txt
```{{exec}}

</details>
