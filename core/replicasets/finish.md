# ⚓ Well done, Captain!

* Controllers loop forever: **watch → compare → act**. Delete a pod, and the ReplicaSet makes a new one.
* A ReplicaSet finds its pods by **labels**, not by name.
* Changing a ReplicaSet's template doesn't touch running pods. A **Deployment** does that for you,
  which is why we use Deployments: next lab.

Next lab: **Core 6 · Roll out the fleet (Deployments)** ⚓
