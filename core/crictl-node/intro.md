# Talk to the engine room

`kubectl` talks to the harbor office. But on the node, the **container runtime** does the real work.
`crictl` lets you talk to it directly, the way you debug a node when the API is down.

A pod called **`lighthouse`** is already running.

Lesson: [1.2B ctr vs nerdctl vs crictl](https://captains-academy.site/course/kubernetes/lesson/1.2B)
