# The ghost that won't leave 🔧

There's a pod called **`ghost-controlplane`** in the `default` namespace.
Try `kubectl delete pod ghost-controlplane`, then look again. 👻

Get rid of it **for good**.

<br>

<details><summary>💡 Hint</summary>

A name ending in `-<nodename>` is a mirror pod: the kubelet recreates it from a file. Which folder does the kubelet on the controlplane watch?

</details>

<details><summary>Solution</summary>

```plain
kubectl get pod ghost-controlplane -o jsonpath='{.metadata.annotations}'; echo
grep -l ghost /etc/kubernetes/manifests/*
```{{exec}}

```plain
rm /etc/kubernetes/manifests/ghost.yaml
kubectl get pods
```{{exec}}

</details>
