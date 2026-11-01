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

## Module 2 · Scheduling
| Lab | Lessons | Level | You will |
|---|---|---|---|
| [manual-scheduling](scheduling/manual-scheduling) | 2.1 | 🟢 | find the missing scheduler, place a pod with nodeName, bring it back |
| [labels-selectors](scheduling/labels-selectors) | 2.2 | 🟢 | equality and set-based selectors, fix a too-wide Service selector |
| [taints-tolerations](scheduling/taints-tolerations) | 2.3 | 🟡 | taint a node, tolerations, fix a typo'd toleration, NoExecute eviction |
| [node-selection](scheduling/node-selection) | 2.4, 2.5 | 🟡 | nodeSelector, required node affinity, fix a case-sensitive affinity |
| [dedicated-nodes](scheduling/dedicated-nodes) | 2.6 | 🟡 | taint + toleration + affinity to dedicate a node |
| [resources](scheduling/resources) | 2.7 | 🟡 | requests/limits, an OOMKilled pod, a pod too big for any node |
| [limits-quotas](scheduling/limits-quotas) | 2.8 | 🟡 | LimitRange defaults, ResourceQuota, read quota errors |
| [daemonsets-static](scheduling/daemonsets-static) | 2.9, 2.10 | 🟡 | DaemonSet on every node, static pod on a worker, remove a ghost static pod |
| [priority-schedulers](scheduling/priority-schedulers) | 2.11-2.13 | 🟡 | PriorityClasses, fix a pod waiting for a missing scheduler |
| [admission](scheduling/admission) | 2.14, 2.15 | 🟡 | read and enable admission plugins on the API server |
| [pending-boss](scheduling/pending-boss) | 2.R | 🔴 | boss: four Deployments Pending for four different reasons |

## Module 10 · Helm
| Lab | Lessons | You will |
|---|---|---|
| [first-release](helm/first-release) | 10.1, 10.2 | install a chart as a release and find what it created |
| [chart-anatomy](helm/chart-anatomy) | 10.2 | read Chart.yaml / values.yaml and render with `helm template` |
| [values-precedence](helm/values-precedence) | 10.3 | combine `-f` and `--set`, upgrade without losing values |
| [bad-upgrade](helm/bad-upgrade) | 10.3 | read `helm history` and roll back a broken upgrade |

Full guide (how it all works, testing, adding packs, troubleshooting): [docs/GUIDE.md](docs/GUIDE.md)

## Layout
Every lab folder is one Killercoda scenario: `index.json` (steps + cluster image), `intro.md`, `finish.md`,
`background.sh` (prepares the cluster, then touches `/tmp/finished`), `foreground.sh` (waits for it),
and `stepN/text.md` + `stepN/verify.sh` (exit 0 = solved). `structure.json` groups labs into courses.

Generators: `tools/gen_core.py`, `tools/gen_sched.py`, `tools/gen_helm.py` (shared helpers in `tools/labkit.py`): edit them, not the folders.

`labs.json` maps lesson codes to lab URLs; the reels repo's `lab_links.py` puts them on the website.
