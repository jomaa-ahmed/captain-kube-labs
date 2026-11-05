Someone opened a `test` workspace and built `dock-test.txt` in it. Close that slipway **completely**:
the workspace must disappear, and so must everything it built.

<br>

<details><summary>💡 Hint</summary>

`terraform workspace delete test` refuses while the workspace still tracks resources. Select it, `terraform destroy`, go back to another workspace, then delete it.

</details>

<details><summary>Solution</summary>

```plain
cd /root/slipways
terraform workspace select test
terraform destroy -auto-approve
terraform workspace select default
terraform workspace delete test
```{{exec}}

</details>
