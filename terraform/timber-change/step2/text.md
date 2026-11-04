A crack in the hull: rebuild it **now**, once, without changing any code and without touching the recipe.
Look at the plan first.

<br>

<details><summary>💡 Hint</summary>

`terraform apply -replace=local_file.hull`. (`terraform taint` is deprecated, and it only marks the resource: nothing is rebuilt until the next apply.)

</details>

<details><summary>Solution</summary>

```plain
cd /root/timber
terraform apply -replace=local_file.hull -auto-approve
```{{exec}}

</details>
