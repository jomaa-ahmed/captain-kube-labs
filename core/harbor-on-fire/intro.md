# The harbor is on fire 🔥

The harbor's web page is down and visitors are lining up. Several things are broken at once,
and nobody tells you what. You have everything from Module 1: pods, ReplicaSets, Deployments, Services,
namespaces, `describe`, `logs`.

* The app lives in namespace **`harbor`** (Deployment and Service **`harbor-web`**).
* The visitors are the Deployment **`visitor`** in namespace **`town`**.

**Rules:** fix what's there. Don't create new Services or Deployments, and don't move anything to another namespace.

Review: [1.R Module 1 review](https://captains-academy.site/course/kubernetes/lesson/1.R)
