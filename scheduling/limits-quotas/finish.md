# ⚓ Well done, Captain!

* **LimitRange**: defaults (and min/max) per container, applied when the pod is created.
* **ResourceQuota**: totals per namespace. Once a quota covers CPU or memory, every pod must declare them, and the LimitRange defaults do that for you.
* A refused pod never exists: the reason is in the **ReplicaSet events**, not in `kubectl get pods`.

Next lab: **Sched 8 · Lamps on every dock (DaemonSets & static pods)** ⚓
