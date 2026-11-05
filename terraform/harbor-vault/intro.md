# Into the vault

In `/root/harbor`, the state is a plain `terraform.tfstate` next to the code. It's time to move the ledger
into the vault: `vault/terraform.tfstate`. (On a real team that's an S3 bucket; the steps are the same.)

Lessons: [8.4 Remote state](https://captains-academy.site/course/terraform/lesson/8.4) · [8.5 Migrating state](https://captains-academy.site/course/terraform/lesson/8.5)
