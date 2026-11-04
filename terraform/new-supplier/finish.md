# ⚒ Well built, Shipwright!

`init` is the only command that downloads providers: a new provider in the code means `init` again (the lock
file gains it, nothing else changes). And only **hashicorp/** providers can skip the source: for every other
company, write `namespace/type` in `required_providers`.

Next lab: **Versions and the lock file** ⚒
