# ⚓ Well done, Captain!

* Deployment → ReplicaSet → Pods: each version gets its own ReplicaSet.
* A rollout replaces pods step by step; `kubectl rollout undo` scales the old ReplicaSet back up.
* Never create bare pods or bare ReplicaSets for an app: use a Deployment.

Next lab: **Core 7 · Give the harbor an address (Services)** ⚓
