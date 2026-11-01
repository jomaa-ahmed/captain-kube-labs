# ⚓ Well done, Captain!

* etcd stores every object under `/registry/<type>/<namespace>/<name>`.
* It runs as a static pod, and only clients with its certificates may talk to it.
* Backups (`etcdctl snapshot save`) are how you save the whole harbor: that comes in Module 5.

Next lab: **Core 4 · Launch your first pods** ⚓
