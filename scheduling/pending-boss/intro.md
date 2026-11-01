# Nobody leaves the harbor 🔥

Four Deployments in namespace **`dock`** (**`alpha`**, **`bravo`**, **`charlie`**, **`delta`**) are all stuck:
every pod is `Pending`, and **each one for a different reason**. Nobody tells you which.

Use your Pending checklist: **scheduler → events → selectors/affinity → taints → resources → schedulerName**.

**Rules:** keep node01's `maintenance` taint, don't delete or recreate the Deployments, keep `alpha`'s and `bravo`'s
nodeSelectors, keep a CPU request on `charlie`, and no `nodeName` shortcuts.

Review: [2.R Module 2 review](https://captains-academy.site/course/kubernetes/lesson/2.R)
