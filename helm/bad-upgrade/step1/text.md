# Read the logbook

The release **`web`** lives in namespace **`fleet`**.

1. Find out why the new pod is unhappy
2. Write the number of the **last good revision** into **`/root/good-revision.txt`**

<br>

<details><summary>💡 Hint</summary>

`kubectl get pods -n fleet` shows the symptom. `helm history <release> -n <ns>` shows the revisions,
and `helm get values <release> -n <ns> --revision N` shows what changed.

</details>

<details><summary>Solution</summary>

```plain
kubectl get pods -n fleet
helm history web -n fleet
```{{exec}}

```plain
helm get values web -n fleet --revision 2
```{{exec}}

Revision 2 set a typo'd image tag (`1.27-tpyo`), so revision 1 is the good one:

```plain
echo 1 > /root/good-revision.txt
```{{exec}}

</details>
