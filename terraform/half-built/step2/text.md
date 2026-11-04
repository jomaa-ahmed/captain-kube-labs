The dock code (`random_password.dock_code`) was shouted across the harbor. 🔐
Get a **new** one: replace that resource, and only that one.

⛔ Don't change `main.tf`. ⛔ The ship keeps its name, the logbook stays.

<br>

<details><summary>💡 Hint</summary>

A plan option forces a replacement without editing the code: `terraform apply -replace=ADDRESS`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/halfbuilt
terraform apply -replace=random_password.dock_code -auto-approve
```{{exec}}

</details>
