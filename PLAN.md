# Captain Kube Labs · first pack: Helm (Module 10)

## Context
A viewer asked for hands-on, HackTheBox-style practice: fix real problems with pods, services and so on, for interview and exam practice.
We compared the options:
- **Own servers:** Sysbox labs cost about €22–75 a month, plus several weeks of building.
- **Killercoda:** €0 for the creator. Users need a free Killercoda account. Sessions last 1 h. Killercoda can't be embedded in the site (it sends `X-Frame-Options: DENY`), so the site links to it.

Decision: start on **Killercoda**, with **Helm (Module 10)** as the first pack.
The same bash setup and verify scripts can move to a Sysbox server later if the labs become popular.

Outcome:
- 4 Helm labs live on Killercoda.
- A "⚓ Practice in the lab" button on lessons 10.1–10.3 on captains-academy.site.
- A repeatable recipe for the other modules.

## What you need (your part, ~20 min, your accounts)
1. **Killercoda account.** Sign in at killercoda.com (GitHub), then go to **Creators → Become a Creator**. Tell me your Killercoda username.
2. **A public GitHub repo** named `captain-kube-labs`. You create it, or I create it with `gh` as jomaa-ahmed if you say so.
3. **Connect the repo.** In your Killercoda creator profile, add the repo and branch `main` (follow Killercoda's on-screen steps). From then on, every push updates the labs.
4. **One SQL line in Supabase.** Run it in the Supabase SQL editor (step 5 below).
5. **Testing.** Sign in to Killercoda in the Browser pane once, so we can test the labs together.

## The 4 Helm labs (my part)
- Each lab builds its own small local chart in `setup.sh` (`helm create` plus edits, or a chart in `assets/`). That avoids depending on public repos: Bitnami's free catalog changed in 2025.
- `setup.sh` installs helm only if it's missing.
- Cluster: `kubernetes-kubeadm-1node`, which starts fastest. Helm doesn't need 2 nodes.
- Each lab has: a story in Captain Kube's voice (harbor metaphors from the reels), steps, a hidden 💡 Hint, a hidden Solution, and verify scripts that check the **cluster result**, so any correct method passes. The finish page has "⚓ Well done, Captain!" plus a link back to the next lesson.

| Lab | Lessons | Task | verify.sh checks |
|---|---|---|---|
| `helm-first-release` | 10.1, 10.2 | Install the local `harbor-web` chart as release `web` in namespace `docks`; find its status and revision | `helm status web -n docks` = deployed; pods Running |
| `helm-chart-anatomy` | 10.2 | Explore the chart (Chart.yaml, values.yaml, templates/), render it with `helm template` to `/root/rendered.yaml` without installing | the file exists, contains a Deployment and Service; no new release was created |
| `helm-values-precedence` | 10.3 | Install with `-f prod.yaml` (replicas 2) **and** `--set` (replicas 3, NodePort) | Deployment has 3 replicas; Service type NodePort; values came via the release (`helm get values`) |
| `helm-bad-upgrade` | 10.3 | Setup leaves revision 2 broken (bad image → ImagePullBackOff). Find it with `helm history` and roll back | latest revision ≥ 3 and `deployed`; image is the good one; pods Running; release not reinstalled (rev 1 still in history) |

Each verify step catches **wrong fixes** too:
- Uninstall + reinstall instead of rollback → fails (history reset).
- `kubectl edit` instead of Helm → fails (Helm values unchanged).

## Repo layout (`C:\Users\Asus\Documents\GitHub\captain-kube-labs`, separate from reels)
```
README.md                     what the labs are + links
PLAN.md                       this plan
structure.json                Killercoda course grouping: "Module 10 · Helm"
helm-first-release/
  index.json                  title, imageid, intro/steps/finish, background setup
  intro.md  finish.md
  setup.sh                    background: build chart, prepare state
  step1/text.md  step1/verify.sh
  step2/...
helm-chart-anatomy/ ...
helm-values-precedence/ ...
helm-bad-upgrade/ ...
```
Lab links will be `https://killercoda.com/<username>/scenario/<lab-folder>`. The exact URL is confirmed after the first push.

## Website: "Practice in the lab" button
1. **Supabase.** Add a column and keep the seed file in step:
   - `ALTER TABLE public.lessons ADD COLUMN IF NOT EXISTS lab_url text;` (you run it in the Supabase SQL editor)
   - Append the same line to `codebase/supabase/setup.sql`, next to the `video_url` addition at line ~161.
2. **Lesson page.** In `codebase/src/routes/course.$slug.lesson.$code.tsx`:
   - Load `lab_url` with the lesson. It sits next to `video_url` at line ~39.
   - Show a "⚓ Practice in the lab" card with the brass/harbor style near the Quiz block (line ~185) when `lab_url` is set. It opens in a new tab and says "free Killercoda account, 1 h session".
   - Check that the Supabase types in `codebase/src/integrations/supabase/` include the new column.
3. **Linking script.** New `.claude/skills/kube/scripts/lab_links.py` reads `captain-kube-labs/labs.json` (`{"10.1": "<url>", ...}`) and PATCHes `lessons.lab_url`. It reuses `sb()` and `site_code()` from `.claude/skills/kube/scripts/publish_site.py`.
4. **Deploy.** Deploy the site the usual way (`codebase/DEPLOY.md`).

## Skill update (so future modules follow the same recipe)
- Add `.claude/skills/kube/references/labs.md` with the lab format, verify rules (check results, catch wrong fixes, hint + solution), naming, and the `labs.json` + `lab_links.py` flow.
- Add one line in SKILL.md pointing to it.

## Order of work
1. You do the account setup (above); I create the repo layout and write the 4 labs.
2. Run `bash -n` on every script; push; Killercoda builds the labs.
3. Test every lab in the Browser pane: solve it the right way → ✅; try the typical wrong fixes → ❌; check setup time is under ~1 min.
4. Add the `lab_url` column, page button and `lab_links.py`; link 10.1–10.3; deploy.
5. Write `labs.md` in the skill and update memory.

Rough effort: about one long session for the labs and testing, plus about half a session for the site button.

## Later (not in this pack)
- **Stamp code:** a code on the finish page that the user types on the site to earn a "Lab done ⚓" stamp (Supabase table + small form).
- **Next packs:** Kustomize (Module 11), then Modules 1–8 with 3–5 labs each.
- **Own Sysbox server:** only if the labs become popular. The same scripts move over.

## Verification
- Each lab, on Killercoda: the right solution passes every CHECK; each listed wrong fix fails; hints and solution render; finish page shows.
- Site: lessons 10.1–10.3 show the button and the link opens the correct lab; other lessons show no button; mobile layout is OK. Checked with the Browser pane on captains-academy.site.
- `lab_links.py`: running it twice leaves the same result.
