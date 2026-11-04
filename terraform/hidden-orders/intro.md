# Hidden orders

In `/root/orders`, Terraform writes `orders.txt`, and a data source reads it to copy it into `crew.txt`.
Nothing in the code tells Terraform the file must exist first, so the very first plan fails.

Try it:
```
cd /root/orders
terraform plan
```

Lesson: [7.1 depends_on](https://captains-academy.site/course/terraform/lesson/7.1)
