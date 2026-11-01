# Sail back

**Roll back** the release `web` to the last good revision.

⚠️ Use Helm's rollback: no `kubectl set image`, no uninstall + reinstall, no new upgrade.
The logbook must keep every revision, and the pod must be running again.

<br>

<details><summary>💡 Hint</summary>

`helm rollback <release> [revision] -n <ns>`. Without a revision number it goes back one step.
A rollback is written in the logbook as a **new** revision.

</details>

<details><summary>Solution</summary>

```plain
helm rollback web 1 -n fleet
```{{exec}}

```plain
helm history web -n fleet
kubectl get pods -n fleet
```{{exec}}

</details>
