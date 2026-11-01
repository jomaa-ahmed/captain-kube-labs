# Give the harbor an address

Pods come and go, and their IPs change. A **Service** is the harbor's fixed address: it finds pods by
**labels** and sends traffic to them.

On deck: Deployments **`web`** and **`api`**, a Service **`web`** that doesn't work, and a pod **`client`**.

Lessons: [1.14 Services](https://captains-academy.site/course/kubernetes/lesson/1.14) · [1.15 NodePort](https://captains-academy.site/course/kubernetes/lesson/1.15) · [1.16 ClusterIP](https://captains-academy.site/course/kubernetes/lesson/1.16) · [1.9 kube-proxy](https://captains-academy.site/course/kubernetes/lesson/1.9)
