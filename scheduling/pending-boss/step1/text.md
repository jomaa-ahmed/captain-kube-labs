# Get every ship out 🔥

Goal: **`alpha`, `bravo`, `charlie` and `delta` all have their pod Running.**

Faults hidden here: **4**.

<br>

<details><summary>💡 Hint</summary>

Start with `kubectl -n dock describe pod <pod>` for each one: the **Events** name the reason ("didn't match node selector", "untolerated taint", "Insufficient cpu"). One pod has **no events at all**: who was supposed to schedule it?

</details>

<details><summary>Solution</summary>

**alpha** wants a node label nobody has: label node01 (or change the selector).

```plain
kubectl label nodes node01 disktype=ssd
```{{exec}}

**bravo** must run on node01, which has a taint: add a toleration.

```plain
kubectl -n dock patch deploy bravo -p '{"spec":{"template":{"spec":{"tolerations":[{"key":"maintenance","operator":"Equal","value":"true","effect":"NoSchedule"}]}}}}'
```{{exec}}

**charlie** requests 64 CPUs: ask for something sensible.

```plain
kubectl -n dock set resources deploy charlie --requests=cpu=250m
```{{exec}}

**delta** waits for a scheduler that doesn't exist.

```plain
kubectl -n dock patch deploy delta -p '{"spec":{"template":{"spec":{"schedulerName":"default-scheduler"}}}}'
kubectl -n dock get pods -o wide
```{{exec}}

</details>
