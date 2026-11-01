# ⚓ Well done, Captain!

* **NoSchedule**: no new pods without a toleration. **PreferNoSchedule**: avoid if possible.
  **NoExecute**: also **evicts** running pods that don't tolerate it.
* A toleration lets a pod **onto** a tainted node; it doesn't attract it. To send a pod somewhere, use a nodeSelector or node affinity.
* The control-plane node is usually tainted `node-role.kubernetes.io/control-plane:NoSchedule`.

Next lab: **Sched 4 · Pick the right dock (nodeSelector & affinity)** ⚓
