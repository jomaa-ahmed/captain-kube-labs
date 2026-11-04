# ⚒ Well built, Shipwright!

A data source is read during plan, so it can't see a file that apply hasn't written yet: `depends_on` makes it
wait. But a reference (`local_file.orders.content`) is an implicit dependency that does the same job, and it's
clearer. References first, `depends_on` for what no reference can show.

Next lab: **Terraform · Shipyard rules** ⚒
