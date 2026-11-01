# ⚓ Captain Kube Labs

Hands-on Kubernetes labs for the Captain Kube course ([captains-academy.site](https://captains-academy.site)).
Each lab runs on a real cluster on [Killercoda](https://killercoda.com/captainkube) (free account, 1 h session).
A CHECK button verifies the **result in the cluster**, so any correct method passes, like the CKA exam.

## Module 1 · Core Concepts
| Lab | Lessons | Level | You will |
|---|---|---|---|
| [cluster-tour](core/cluster-tour) | 1.1, 1.5, 1.8 | 🟢 | find the control plane, the static pods and the kubelet |
| [crictl-node](core/crictl-node) | 1.2 B | 🟢 | inspect containers and pod sandboxes with crictl |
| [etcd-peek](core/etcd-peek) | 1.3, 1.4 | 🟡 | run etcdctl with etcd's certificates and read the /registry keys |
| [pods-first](core/pods-first) | 1.10, 1.11 | 🟢 | write a pod in YAML, rescue a broken pod, add a sidecar |
| [replicasets](core/replicasets) | 1.6, 1.12 | 🟡 | watch the control loop, scale, fix a ReplicaSet with a bad image |
| [deployments](core/deployments) | 1.13 | 🟡 | create, roll out and undo a broken rollout |
| [services-fix](core/services-fix) | 1.9, 1.14-1.16 | 🟡 | fix a Service with no endpoints, NodePort 30080, ClusterIP backend |
| [namespaces-dns](core/namespaces-dns) | 1.18 | 🟡 | switch namespaces, full DNS names, fix a cross-namespace client |
| [imperative-yaml](core/imperative-yaml) | 1.19, 1.20 | 🟡 | generate YAML with --dry-run, kubectl explain, apply |
| [harbor-on-fire](core/harbor-on-fire) | 1.R | 🔴 | boss: find and fix four hidden faults |

## Module 10 · Helm
| Lab | Lessons | You will |
|---|---|---|
| [first-release](helm/first-release) | 10.1, 10.2 | install a chart as a release and find what it created |
| [chart-anatomy](helm/chart-anatomy) | 10.2 | read Chart.yaml / values.yaml and render with `helm template` |
| [values-precedence](helm/values-precedence) | 10.3 | combine `-f` and `--set`, upgrade without losing values |
| [bad-upgrade](helm/bad-upgrade) | 10.3 | read `helm history` and roll back a broken upgrade |

## Layout
Every lab folder is one Killercoda scenario: `index.json` (steps + cluster image), `intro.md`, `finish.md`,
`background.sh` (prepares the cluster, then touches `/tmp/finished`), `foreground.sh` (waits for it),
and `stepN/text.md` + `stepN/verify.sh` (exit 0 = solved). `structure.json` groups labs into courses.

Generators: `tools/gen_core.py`, `tools/gen_helm.py` (shared helpers in `tools/labkit.py`): edit them, not the folders.

`labs.json` maps lesson codes to lab URLs; the reels repo's `lab_links.py` puts them on the website.
