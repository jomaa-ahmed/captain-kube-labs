# ⚓ Well done, Captain!

* No scheduler = new pods stay `Pending` with no events.
* `spec.nodeName` places a pod directly on a node (only at creation). The scheduler itself does it with a **Binding** object.
* The scheduler is a static pod: its manifest lives in `/etc/kubernetes/manifests`.
* When it runs, it **filters** out nodes that can't take the pod, **scores** the rest and binds the pod to the winner.

Next lab: **Sched 2 · Find ships by their flags (labels)** ⚓
