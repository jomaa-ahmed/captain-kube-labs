# ⚒ Well built, Shipwright!

Terraform only sees addresses: a rename alone is destroy + create. A `moved` block changes the address and keeps
the real object, with a plan and a record every environment can apply. Keep moved blocks until all have applied them.

Next lab: **Terraform · Hand over** ⚒
