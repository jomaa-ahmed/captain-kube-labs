Save a **DEBUG** log of `terraform plan` into `/root/handover/plan.log`, using Terraform's own logging.

<br>

<details><summary>💡 Hint</summary>

Two environment variables: `TF_LOG=DEBUG TF_LOG_PATH=./plan.log terraform plan`. TF_LOG_PATH alone logs nothing.

</details>

<details><summary>Solution</summary>

```plain
cd /root/handover
TF_LOG=DEBUG TF_LOG_PATH=./plan.log terraform plan
```{{exec}}

</details>
