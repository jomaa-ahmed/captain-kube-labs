# Help the buyer 🔧

The Deployment **`buyer`** in namespace **`docks`** can't reach the shop. Read its logs, find out why,
and fix the **buyer** so its logs say `OK reached shop`.

⚠️ Don't move or copy the shop: fix the buyer.

<br>

<details><summary>💡 Hint</summary>

`kubectl -n docks logs deploy/buyer` shows which URL it uses. The URL comes from an environment variable: `kubectl -n docks set env deploy/buyer KEY=value` changes it.

</details>

<details><summary>Solution</summary>

```plain
kubectl -n docks logs deploy/buyer --tail=3
```{{exec}}

```plain
kubectl -n docks set env deploy/buyer SHOP_URL=http://shop.market.svc.cluster.local
kubectl -n docks rollout status deploy/buyer
sleep 5; kubectl -n docks logs deploy/buyer --tail=3
```{{exec}}

</details>
