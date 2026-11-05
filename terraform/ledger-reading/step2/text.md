The state holds every attribute in plain text, and a second apply also writes `terraform.tfstate.backup`.
Create a `.gitignore` so that Git ignores **every** state file and the `.terraform/` folder, but still tracks `main.tf`.

Check with `git status`.

<br>

<details><summary>💡 Hint</summary>

One pattern covers the state and its backup: `*.tfstate*`. Add `.terraform/` on a second line.

</details>

<details><summary>Solution</summary>

```plain
cd /root/ledger
printf '*.tfstate*\n.terraform/\n' > .gitignore
git status --short
```{{exec}}

</details>
