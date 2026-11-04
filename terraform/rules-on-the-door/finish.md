# ⚒ Well built, Shipwright!

The terraform block is read **first**, before variables and locals exist, so it only takes fixed values:
`required_version`, `required_providers`, and `backend` (or `cloud`). Per-environment backend settings come
from `terraform init -backend-config=...` (Module 8).

Next lab: **BOSS · Shipyard in trouble** ⚒
