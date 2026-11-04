# Timber change

In `/root/timber`, the hull doesn't mention the recipe, so when `var.recipe` changes from oak to pine,
Terraform does nothing. The shipwright's rule: new timber, new hull.

Lesson: [7.4 replace_triggered_by](https://captains-academy.site/course/terraform/lesson/7.4)
