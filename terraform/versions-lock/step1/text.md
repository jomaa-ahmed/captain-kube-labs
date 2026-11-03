Make `terraform init` succeed with a **2.4.x** version of the local provider.

⛔ Keep the constraint `~> 2.4.0`. ⛔ Don't edit or delete `.terraform.lock.hcl` by hand.

<br>

<details><summary>💡 Hint</summary>

Read init's error: the lock file still says 2.9.x. `init -upgrade` picks the newest version the constraint allows and rewrites the lock.

</details>

<details><summary>Solution</summary>

```plain
cd /root/versions
terraform init || true
terraform init -upgrade
```{{exec}}

</details>
