Remove the token from every `.tf` file. The provider must keep its **owner** setting, and
`terraform validate` must still succeed.

Then write in `/root/answers/token_env.txt` the name of the **environment variable** the GitHub provider
reads its token from, so the crew can set it in their terminal or pipeline instead.

<br>

<details><summary>💡 Hint</summary>

Delete the `token = ...` line, keep `owner`. The provider's docs (and its error messages) name the variable: `GITHUB_TOKEN`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/secrets
sed -i '/token *=/d' provider.tf
terraform validate
mkdir -p /root/answers
echo GITHUB_TOKEN > /root/answers/token_env.txt
```{{exec}}

</details>
