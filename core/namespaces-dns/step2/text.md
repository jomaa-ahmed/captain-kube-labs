# The full address

Write the **fully qualified DNS name** of the Service `shop` in namespace `market`
into **`/root/shop-fqdn.txt`**.

<br>

<details><summary>💡 Hint</summary>

The pattern is `<service>.<namespace>.svc.<cluster-domain>`. The cluster domain is usually `cluster.local`.

</details>

<details><summary>Solution</summary>

```plain
echo shop.market.svc.cluster.local > /root/shop-fqdn.txt
```{{exec}}

</details>
