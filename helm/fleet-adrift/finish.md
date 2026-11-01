# ⚓ Well done, Captain!

You rescued the whole armada:

1. Found Helm's release history stored in **`helm.sh/release.v1` Secrets** inside the release's namespace
2. Removed `ghost` cleanly with **`helm uninstall`**
3. Rolled **`beacon`** back across two bad upgrades to revision 1 (creating revision 4)
4. Upgraded **`compass`** with `-f /root/compass-prod.yaml` and `--set image.tag=1.27-alpine`

Module 10 conquered. 🏆 Next on the course: [Module 11 · Kustomize](https://captains-academy.site/course/kubernetes/lesson/11.T)
