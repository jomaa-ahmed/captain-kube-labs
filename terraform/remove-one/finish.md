# ⚒ Well built, Shipwright!

Deleting a block and applying is how you retire one resource every day.
`terraform destroy` removes **everything** in the state, and nothing that isn't in it (like neighbor.txt).
`plan -destroy -out` lets a team review the teardown first; `terraform apply teardown.tfplan` would run it.

Next lab: **New supplier** ⚒
