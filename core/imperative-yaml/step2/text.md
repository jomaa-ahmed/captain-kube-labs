# Look it up

The beacon must shut down quickly. Find the **pod-level field** that sets how many seconds a pod gets
to stop gracefully, and set it to **15** in `/root/beacon.yaml`.

Use `kubectl explain`, not Google. 😉

<br>

<details><summary>💡 Hint</summary>

`kubectl explain pod.spec | grep -i grace`, then `kubectl explain deployment.spec.template.spec.<field>`. It goes next to `containers:` in the pod template.

</details>

<details><summary>Solution</summary>

```plain
kubectl explain pod.spec | grep -i -A2 grace
```{{exec}}

```plain
sed -i 's/^      containers:/      terminationGracePeriodSeconds: 15\n      containers:/' /root/beacon.yaml
grep -B1 -A2 termination /root/beacon.yaml
```{{exec}}

</details>
