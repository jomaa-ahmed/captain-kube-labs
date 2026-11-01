# ⚓ Captain Kube Labs · the complete guide

This guide explains everything about the hands-on labs: what they are, how all the pieces connect,
how a lab works inside, how to test one, how to add a new pack and what to do when something breaks.

---

## 1. The idea in one minute

The Captain Kube course teaches with short videos. The labs add **practice on a real Kubernetes cluster**.

1. A learner watches a lesson on **captains-academy.site**.
2. Under the video there is a card **"⚓ Practice in the lab"**.
3. The card opens a lab on **Killercoda** in a new tab. Killercoda starts a real cluster just for that learner.
4. The learner reads the task on the left and types commands in the terminal on the right.
5. A **CHECK** button tells them if they solved it. If they're stuck, they open 💡 **Hint** or **Solution**.

Many labs are **"something is broken, fix it"** challenges (HackTheBox style), because that's how real work and the CKA exam feel.
Each module ends with a 🔴 **boss lab**: several hidden faults, and only a goal.

**Cost:** €0. Killercoda pays for the clusters. Learners need a free Killercoda account. Free sessions last 1 hour.

---

## 2. How the pieces connect

```
 You / Claude                    GitHub                         Killercoda                     Learner
 ───────────                     ──────                         ──────────                     ───────
 tools/gen_*.py  ──generate──▶  captain-kube-labs repo  ──webhook──▶  killercoda.com/captainkube  ◀── opens lab
 (lab source)       folders      (jomaa-ahmed)             on push     builds the scenarios          from the site
                                                                                                    ▲
 labs.json  ──lab_links.py──▶  Supabase lessons.lab_url  ──▶  captains-academy.site lesson page ────┘
                                                                ("Practice in the lab" card)
```

| Piece | Where | What it does |
|---|---|---|
| **Lab source (generators)** | `captain-kube-labs/tools/gen_*.py` | Python files that write every lab folder. **Edit these, never the folders by hand.** |
| **Shared helpers** | `tools/labkit.py` | Writes a lab (`lab()`), code blocks (`cmd()`), course order (`COURSES`, `structure()`). |
| **Lab folders** | `core/`, `scheduling/`, `helm/` | The generated scenarios Killercoda reads. |
| **GitHub repo** | github.com/jomaa-ahmed/captain-kube-labs (public) | Killercoda reads it with a **read-only deploy key**. A **webhook** tells Killercoda to sync on every push. |
| **Killercoda profile** | killercoda.com/captainkube | Your creator page: Title "Captain Kube", logo, link to the site, searchable. |
| **labs.json** | repo root | Maps lesson codes to lab URLs, e.g. `"1.13": ".../course/core/deployments"`. Several lessons can share one lab. |
| **lab_links.py** | `reels/.claude/skills/kube/scripts/` | Reads `labs.json` and writes `lab_url` on each lesson in Supabase. Safe to run any time (running it twice changes nothing). |
| **Website card** | `reels/codebase/src/routes/course.$slug.lesson.$code.tsx` | Shows "⚓ Practice in the lab" when a lesson has a `lab_url`. Opens in a new tab (Killercoda can't be embedded: it forbids iframes). |
| **Database column** | Supabase `lessons.lab_url` (`setup.sql` section 0005) | Holds the link. No site redeploy is needed when links change. |

---

## 3. What's live now

| Course on Killercoda | Labs | Lessons linked |
|---|---|---|
| Module 1 · Core Concepts (`core`) | 10 | 19 |
| Module 2 · Scheduling (`scheduling`) | 11 | 16 |
| Module 10 · Helm (`helm`) | 4 | 3 |
| **Total** | **25** | **38** |

Full lab lists with levels are in the repo [README](../README.md).

Lessons without a lab: trailers (`x.T`) and a few pure-theory lessons (1.2 A, 1.7, 1.17). Their ideas are covered in the
finish pages of nearby labs.

---

## 4. Inside one lab

Every lab folder is one Killercoda **scenario**:

```
core/deployments/
  index.json        title, steps, cluster type (1 node or 2 nodes)
  intro.md          the story, in Captain Kube's voice, with links to the lessons
  background.sh     runs first, hidden: builds the scene (apps, broken objects), then touches /tmp/finished
  foreground.sh     shows "⚓ Captain Kube is preparing your harbor..." until /tmp/finished exists
  step1/text.md     the task + 💡 Hint + Solution (click a command to run it)
  step1/verify.sh   the CHECK button: exit 0 = solved, anything else = not yet
  step3/background.sh   (optional) runs when the learner reaches step 3, e.g. pushes a broken rollout
  finish.md         "⚓ Well done, Captain!" + the 3 key ideas + the next lab
```

**The two cluster types**

* `kubernetes-kubeadm-1node`: one node called `controlplane`. Starts fastest.
* `kubernetes-kubeadm-2nodes`: `controlplane` + `node01`. Used for scheduling labs. `ssh node01` works from the terminal.

**The rules every lab follows**

1. **Check the result, not the command.** verify.sh looks at the cluster (`kubectl … -o jsonpath`), so any correct method passes.
2. **Make the wrong fix fail.** Examples:
   * deleting and recreating an object instead of fixing it (setup saves the object's UID and verify compares it)
   * `kubectl create` instead of `apply` (no `last-applied-configuration` annotation)
   * a new `set image` instead of `rollout undo` (revision count)
   * removing a taint that the task says to keep
3. **Say what isn't allowed** in the task text (⚠️ lines), so the learner knows the rules.
4. **Answers in files** (`/root/x.txt`) are compared after removing spaces and newlines.
5. **Levels:** 🟢 Easy · 🟡 Medium · 🔴 Hard (boss). 🔧 marks a "fix it" step.
6. **No outside dependencies:** setup builds everything (local Helm charts, small images from Docker Hub: nginx, busybox, pause, polinux/stress).

---

## 5. How to test a lab (your checklist)

Open the lab from the site card or from killercoda.com/captainkube.

1. Wait for **"⚓ Ready"** in the terminal (the first start after a push can be slower while Killercoda's caches sync).
2. Click **CHECK** before doing anything. It must say **not correct**.
3. Try the **wrong fix** named in the task (⚠️ line). CHECK must **fail**.
4. Solve it properly (the Solution box is fine). CHECK must **pass** and open the next step.
5. Check that 💡 Hint and Solution open and that clicking a command runs it.
6. On the finish page, check the text and the "Next lab" name.

**Known timing behaviour (not bugs):**

* After deleting pods, terminating pods can make CHECK fail for a few seconds. Click CHECK again.
* For labs where a client prints logs every 3 seconds (Core 8, Core 10), wait about 5 seconds after the fix.
* After editing the API server manifest (Sched 10), `kubectl` is offline for up to a minute.

**If something is wrong**, send Claude: the lab name, the step, what you typed, and what happened
(a screenshot or the terminal text). If the setup seems stuck, also run `cat /var/log/killercoda/*` and send the output.

---

## 6. How a change goes live

```
edit tools/gen_<pack>.py  →  python tools/gen_<pack>.py  →  bash -n on every .sh  →  git commit + push
        →  GitHub webhook  →  Killercoda syncs (a minute or two)  →  the lab is updated for new sessions
```

* Check the sync on Killercoda: **Creator → Repository → Git Sync At / Git Commit** shows the last synced commit.
* GitHub shows each webhook delivery under **repo Settings → Webhooks → Recent deliveries** (200 = OK).

---

## 7. How to add a new pack (for example Module 3)

1. **Read the lessons** in `reels/.claude/skills/kube/references/curriculum.md` and pick 3–5 hands-on skills per module, plus a 🔴 boss.
2. **Create `tools/gen_<name>.py`**, copying the shape of `gen_core.py` or `gen_sched.py`:
   * one `lab(...)` call per lab: folder, title with level, description, intro, steps, finish, background
   * each step: `title`, `text`, `hint`, `solution`, `verify`, optional `background`
   * end with `labkit.structure(<dir>, [lab order])`
3. **Add the course** to `COURSES` in `tools/labkit.py` (this sets the order on the Killercoda profile).
4. **Generate and check:** `python tools/gen_<name>.py`, then `bash -n` on every `.sh`.
5. **Add the links** to `labs.json` (lesson code → lab URL) and a table to `README.md`.
6. **Push.** Check the new course appears on killercoda.com/captainkube.
7. **Link the site:** `python lab_links.py` (in `reels/.claude/skills/kube/scripts/`).
8. **Test** with the checklist in section 5.

Writing rules for Claude live in the kube skill: `reels/.claude/skills/kube/references/labs.md`.

---

## 8. Accounts and settings

| What | Value | Who manages it |
|---|---|---|
| Killercoda creator | `captainkube` (killercoda.com/captainkube) | you |
| GitHub repo | `jomaa-ahmed/captain-kube-labs`, branch `main`, public | Claude can push (gh signed in as jomaa-ahmed) |
| Deploy key | "killercoda", read-only | on the repo (Settings → Deploy keys) |
| Webhook | `webhook.killercoda.com/...`, push events, JSON, with secret | on the repo (Settings → Webhooks) |
| Supabase column | `lessons.lab_url` | written by `lab_links.py` with the service key in `reels/.env` |

**Security notes**

* Never commit `.env` or paste keys in chat.
* The webhook secret only lets someone trigger a sync. If you want a new one, regenerate it on Killercoda and update the GitHub webhook.
* The deploy key is read-only: Killercoda can read the repo, never change it.

---

## 9. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| A new lab doesn't appear on Killercoda | sync failed or a JSON error | Look at Creator → Repository (Git Sync At, errors). Check the latest webhook delivery on GitHub. Validate `index.json` / `structure.json`. |
| Webhook shows 400 | Killercoda repo settings not saved | Save the repository page on Killercoda again, then push. |
| Setup never shows "Ready" | a `background.sh` command waits forever (image pull, wrong name) | `cat /var/log/killercoda/*` in the lab terminal; fix the generator; push. |
| CHECK fails although it's solved | verify too strict or timing | Click again after a few seconds; if it still fails, send Claude the output of the commands in `verify.sh`. |
| Card missing on a lesson | no entry in `labs.json`, or `lab_links.py` not run | Add the entry, run `lab_links.py`. |
| Card links to the wrong lab | wrong URL in `labs.json` | Fix it, run `lab_links.py` (it updates and clears links). |

---

## 10. Limits and what's next

**Killercoda limits for learners:** free plan = 1 hour per session and 1 lab at a time; paid plan = 4 hours and 3 labs.
You don't get learner data from Killercoda.

**Planned**

* Packs for Modules 3–9 and Kustomize (Module 11), one module at a time, each with a 🔴 boss lab.
* **Stamp code:** the finish page shows a code that the learner types on the site to earn a "Lab done ⚓" stamp.
* **Own lab servers (Sysbox)** only if the labs get very popular: the same bash scripts can move over.
  Rough cost: ~€22/month for ~8 learners at the same time, ~€40–75/month for ~40.
