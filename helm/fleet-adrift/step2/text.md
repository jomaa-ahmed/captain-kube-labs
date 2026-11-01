# Rescue beacon and compass 🔥

Bring both remaining releases in **`armada`** back to health (faults hidden here: **3**):

* **`beacon`**: check its revision history, find the revision where it worked (image `nginx:1.27`, service port `80`),
  and **roll `beacon` back** to that revision with Helm (don't uninstall or run a new upgrade).
* **`compass`**: upgrade it from `/root/charts/harbor-web` using **`/root/compass-prod.yaml`**, and fix the broken
  image tag so `compass` runs **2 ready pods** with image **`nginx:1.27-alpine`**, pod label **`tier=nav`**,
  and a **`NodePort`** Service.

<br>

<details><summary>💡 Hint</summary>

For `beacon`: `helm history beacon -n armada` and `helm get values beacon -n armada --revision N`, then `helm rollback beacon <rev> -n armada`. For `compass`: look at `/root/compass-prod.yaml` (`1.27-alpin` is missing an `e`), then run `helm upgrade compass /root/charts/harbor-web -n armada -f /root/compass-prod.yaml --set image.tag=1.27-alpine`.

</details>

<details><summary>Solution</summary>

```plain
helm history beacon -n armada
helm get values beacon -n armada --revision 1
helm rollback beacon 1 -n armada
```{{exec}}

```plain
cat /root/compass-prod.yaml
helm upgrade compass /root/charts/harbor-web -n armada -f /root/compass-prod.yaml --set image.tag=1.27-alpine
kubectl get pods,svc -n armada
```{{exec}}

</details>
