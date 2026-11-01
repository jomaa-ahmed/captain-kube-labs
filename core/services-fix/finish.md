# ⚓ Well done, Captain!

* A Service finds pods by **selector**; no matching labels = no endpoints = nothing answers.
* `port` is the Service's port, `targetPort` the container's, `nodePort` (30000-32767) the one on every node.
* kube-proxy writes the rules on each node that turn the Service IP into pod IPs.
* **LoadBalancer** stays `<pending>` without a cloud (or MetalLB) to hand out the external IP,
  but it already works as a NodePort underneath.

Next lab: **Core 8 · Sail between harbors (Namespaces)** ⚓
