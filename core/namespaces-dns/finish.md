# ⚓ Well done, Captain!

* Same namespace: `http://shop`. Another namespace: `http://shop.market` or the full
  `shop.market.svc.cluster.local`.
* `kubectl config set-context --current --namespace=…` saves typing `-n` all day (very useful in the exam).
* Namespaces separate names, not networks: any pod can reach any Service unless a NetworkPolicy says no.

Next lab: **Core 9 · Write YAML the fast way** ⚓
