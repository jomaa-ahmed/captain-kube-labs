# ⚒ Well built, Shipwright!

A **resource** is built and owned: Terraform would have overwritten the register. A **data** source only reads
(`data.TYPE.NAME`), and it lands in the state as a read, not as something to manage. And computed attributes
like `id` are filled in during apply: references carry them along.

Next lab: **Fill the blanks** ⚒
