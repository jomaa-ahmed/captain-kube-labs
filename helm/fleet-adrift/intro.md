# The fleet is adrift 🔥

Three Helm releases in namespace **`armada`** are in a mess after a night watch gone wrong:
* **`ghost`** is a leftover test release that shouldn't be in the harbor at all.
* **`beacon`** was upgraded twice and both upgrades broke it.
* **`compass`** lost its production settings from **`/root/compass-prod.yaml`** (and that file has a bug of its own).

**Rules:** use Helm for every change—no `kubectl delete deploy`, no `kubectl set image`, no `kubectl edit`.

Review: [10.R Module 10 review](https://captains-academy.site/course/kubernetes/lesson/10.R)
