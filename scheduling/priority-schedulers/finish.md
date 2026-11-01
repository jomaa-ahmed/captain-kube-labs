# ⚓ Well done, Captain!

* Higher **priority** = scheduled first; when nodes are full, the scheduler may **preempt** (evict) lower-priority pods.
* Every pod has a `schedulerName` (default `default-scheduler`). A name no scheduler answers to = `Pending` with no events.
* One scheduler can run several **profiles**, each a set of plugins at the queue, filter, score and bind stages.

Next lab: **Sched 10 · The harbor gate (admission controllers)** ⚓
