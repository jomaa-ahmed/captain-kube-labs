# ⚓ Well done, Captain!

* A **DaemonSet** runs one pod per (matching) node, and adds one automatically when a node joins. It needs a toleration to run on tainted nodes.
* **Static pods** come from files in the kubelet's `staticPodPath`; the API only shows a read-only **mirror pod** named `<pod>-<node>`.
* Delete the file to delete a static pod.

Next lab: **Sched 9 · Who sails first (priority & schedulers)** ⚓
