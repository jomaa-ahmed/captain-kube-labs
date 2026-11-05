# ⚒ Well built, Shipwright!

Each workspace keeps its own state (`terraform.tfstate.d/<name>/`), and `terraform.workspace` names it in the code.
A workspace with resources can't be deleted: destroy first. And for separate credentials, use separate configurations.

Next lab: **BOSS · The vault** ⚒
