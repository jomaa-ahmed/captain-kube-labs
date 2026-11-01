# Let the visitors in 🔥

The harbor answers again, but the visitors still can't get in.
Goal: `kubectl -n town logs deploy/visitor` says **`OK harbor reached`**.

Faults hidden here: **1**.

<br>

<details><summary>💡 Hint</summary>

Read the visitor's logs: which address does it use? Which namespace is it in, and which namespace is the harbor in?

</details>

<details><summary>Solution</summary>

```plain
kubectl -n town logs deploy/visitor --tail=3
```{{exec}}

```plain
kubectl -n town set env deploy/visitor TARGET=http://harbor-web.harbor.svc.cluster.local
kubectl -n town rollout status deploy/visitor
sleep 5; kubectl -n town logs deploy/visitor --tail=3
```{{exec}}

</details>
