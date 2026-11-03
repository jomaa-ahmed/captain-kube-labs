Make the manifest's content **`Ship: <the pet's id>`**, using a **reference** to the random pet,
then apply. Watch the order of the *Creating...* lines.

⛔ Don't type the pet name into the file: the blueprint must reference it.

<br>

<details><summary>💡 Hint</summary>

A reference is `type.name.attribute`. Inside a string: `"Ship: ${random_pet.ship.id}"`.

</details>

<details><summary>Solution</summary>

```plain
cd /root/references
sed -i 's/CHANGE-ME/${random_pet.ship.id}/' main.tf
terraform init
terraform apply -auto-approve
```{{exec}}

</details>
