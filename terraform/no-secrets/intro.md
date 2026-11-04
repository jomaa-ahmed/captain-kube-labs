# No secrets in the blueprint

The crew in `/root/secrets` manages its GitHub repositories with the `integrations/github` provider.
An apprentice pasted a **token** straight into `provider.tf`. That file is about to be pushed to Git,
and Git never forgets.

Lesson: [4.4 Configuring a provider](https://captains-academy.site/course/terraform/lesson/4.4)
