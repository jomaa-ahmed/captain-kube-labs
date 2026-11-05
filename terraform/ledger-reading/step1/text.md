Find the real name (the `id`) of `random_pet.ship` and write it, alone, into `/root/ledger/answer.txt`.

⛔ Read it the Terraform way, not by opening `terraform.tfstate` in an editor.

<br>

<details><summary>💡 Hint</summary>

`terraform state show random_pet.ship` prints its attributes. Copy the `id` value (without quotes): `echo some-name > answer.txt`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/ledger
terraform state show -no-color random_pet.ship
terraform show -json | $PY -c "import json,sys; print([r['values']['id'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > answer.txt
```{{exec}}

</details>
