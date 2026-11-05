# ⚒ Well built, Shipwright!

A module is a folder of .tf files; the root calls it with a `module` block (label, `source`, inputs) and needs
`terraform init` for every new call. Resources inside get addresses like `module.kestrel.local_file.this`,
and only outputs come back: `module.kestrel.file`.

Next lab: **Terraform · Sealed kit** ⚒
