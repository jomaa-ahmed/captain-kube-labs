# ⚓ Captain Kube Labs

Hands-on Kubernetes labs for the Captain Kube course ([captains-academy.site](https://captains-academy.site)).
Each lab runs on a real cluster on [Killercoda](https://killercoda.com/captainkube) (free account, 1 h session).
A CHECK button verifies the **result in the cluster**, so any correct method passes, like the CKA exam.

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

`labs.json` maps lesson codes to lab URLs; the reels repo's `lab_links.py` puts them on the website.
