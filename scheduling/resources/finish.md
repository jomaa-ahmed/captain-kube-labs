# ⚓ Well done, Captain!

* The scheduler places pods by **requests**; a request bigger than any node's free capacity = `Pending` ("Insufficient cpu").
* Over the **memory limit** → the container is **OOMKilled** and restarted.
* Over the **CPU limit** → the container is only **throttled**, never killed.

Next lab: **Sched 7 · Harbor rules (LimitRange & ResourceQuota)** ⚓
