# ⚓ Well done, Captain!

* The control plane (apiserver, etcd, scheduler, controller-manager) runs as **static pods** from
  `/etc/kubernetes/manifests`.
* The **kubelet** is a systemd service on every node: it reads that folder and starts the pods.
* That's why kubeadm can't deploy the kubelet for you: something has to run first.

Next lab: **Core 2 · Talk to the engine room** ⚓
