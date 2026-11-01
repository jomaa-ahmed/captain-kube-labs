# The hungry ship sinks 🔧

The pod **`hungry`** keeps restarting. It really needs about **150 MB** of memory to do its job.

1. Write the **reason** its container was killed into **`/root/hungry-reason.txt`** (one word, as Kubernetes shows it)
2. Fix it so `hungry` runs **without restarting**: give it a memory limit of **256Mi**. Keep its command as it is.

<br>

<details><summary>💡 Hint</summary>

`kubectl describe pod hungry` → **Last State** shows the reason. Limits of a running pod can't simply be edited: export the YAML, change the limit, and recreate it (`kubectl replace --force -f`).

</details>

<details><summary>Solution</summary>

```plain
kubectl describe pod hungry | grep -A3 'Last State'
echo OOMKilled > /root/hungry-reason.txt
```{{exec}}

```plain
kubectl get pod hungry -o yaml > /root/hungry.yaml
sed -i 's/memory: 100Mi/memory: 256Mi/' /root/hungry.yaml
kubectl replace --force -f /root/hungry.yaml
kubectl get pod hungry -w
```{{exec}}

</details>
