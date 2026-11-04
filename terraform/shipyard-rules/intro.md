# Shipyard rules

`/root/rules` builds three things: a **dock** (replaced whenever `var.build` changes), the **ledger** and the
**hull**. Each needs a different shipyard rule, in its `lifecycle` block.

Lessons: [7.2 create_before_destroy](https://captains-academy.site/course/terraform/lesson/7.2) · [7.3 prevent_destroy and ignore_changes](https://captains-academy.site/course/terraform/lesson/7.3)
