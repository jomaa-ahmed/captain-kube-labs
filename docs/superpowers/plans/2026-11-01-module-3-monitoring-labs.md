# Module 3 (Logging & Monitoring) Labs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish the complete hands-on Killercoda lab pack for Module 3 (Logging & Monitoring), providing interactive practice for lessons 3.1, 3.2, and review 3.R on captains-academy.site.

**Architecture:** Python scenario generator `tools/gen_monitor.py` using shared `labkit.py` primitives to generate 3 self-contained Killercoda scenarios (`monitor/metrics-top`, `monitor/app-logs`, `monitor/night-watch`). Course registration in `structure.json` and course ordering in `labkit.COURSES`, with links mapped in `labs.json` and synced to the Supabase database via `lab_links.py`.

**Tech Stack:** Python 3, Bash, Kubernetes (kubeadm v1.31+, metrics-server v0.7.2), JSON, Git, Supabase.

**Spec:** `docs/superpowers/specs/2026-11-01-module-3-monitoring-labs-design.md`

## Global Constraints

- Generate scenarios only via `tools/gen_monitor.py`; never hand-edit files in `monitor/`.
- Cluster backend: `kubernetes-kubeadm-1node`.
- All `background.sh` scripts must begin with `kubectl wait --for=condition=Ready node --all --timeout=300s` and conclude with `touch /tmp/finished`.
- Every `verify.sh` must check cluster state, not command strings typed by the learner.
- All `.sh` files must pass syntax validation (`bash -n`).
- Every wrong-fix loophole identified in the spec must fail verification.

## Review Focus

- Metrics server startup: scraping fails without `--kubelet-insecure-tls` on kubeadm clusters; verify `background.sh` applies this flag and waits for metrics availability.
- Multi-container pod logging: verify that `verify.sh` for `-c` ensures the student selected `radio` rather than defaulting to `announcer`.
- CrashLoopBackOff `--previous`: verify `scout` and `siren` pods preserve crash state so `kubectl logs -p` retrieves the crash message reliably.
- `top` sorting: verify `busiest-pod.txt` test accurately identifies the highest CPU user without false positives from temporary spikes.
- In-place fixes: verify that deleting/recreating deployments fails the boss lab UID checks.

---

### Task 1: Register Module 3 in `tools/labkit.py`

**Files:**
- Modify: `tools/labkit.py:8-13`
- Test: `tools/labkit.py`

**Interfaces:**
- Consumes: `labkit.COURSES`
- Produces: `("monitor", "Captain Kube · Module 3 · Logging & Monitoring")` entry in `COURSES`

- [ ] **Step 1: Write a test check for COURSES registration**
Verify `COURSES` contains `("monitor", ...)` between `scheduling` and `helm`.

- [ ] **Step 2: Run test to verify it fails**
Run: `python -c "import labkit; assert any(c[0] == 'monitor' for c in labkit.COURSES)"`
Expected: AssertionError

- [ ] **Step 3: Update `COURSES` in `tools/labkit.py`**
Insert `("monitor", "Captain Kube · Module 3 · Logging & Monitoring")` in `COURSES`.

- [ ] **Step 4: Run test to verify it passes**
Run: `python -c "import labkit; assert any(c[0] == 'monitor' for c in labkit.COURSES); print('OK')"`
Expected: OK

- [ ] **Step 5: Commit**
```bash
git add tools/labkit.py
git commit -m "feat(labkit): register Module 3 Logging & Monitoring course"
```

---

### Task 2: Scaffold `tools/gen_monitor.py` and Lab 1 (`metrics-top`)

**Files:**
- Create: `tools/gen_monitor.py`
- Output directory: `monitor/metrics-top/`

**Interfaces:**
- Consumes: `labkit.lab()`, `labkit.cmd()`, `labkit.D()`, `labkit.structure()`
- Produces: Scenario `monitor/metrics-top` with 3 steps

- [ ] **Step 1: Define shared metrics-server installer and background setup**
Write `INSTALL_METRICS_SERVER` logic in `tools/gen_monitor.py` applying `components.yaml` with `--kubelet-insecure-tls` and waiting for deployment readiness.

- [ ] **Step 2: Define Lab 1 (`metrics-top`)**
Add `metrics-top` scenario with:
- Step 1: `kubectl top pods -n fleet --sort-by=cpu` -> `/root/busiest-pod.txt`
- Step 2: `kubectl top node` -> `/root/node-cpu.txt`
- Step 3: `kubectl top pod freighter -n fleet --containers` -> `/root/heavy-container.txt`

- [ ] **Step 3: Run generator and verify output files**
Run: `python tools/gen_monitor.py`
Verify `monitor/metrics-top/index.json`, `background.sh`, and `step*/verify.sh` exist.

- [ ] **Step 4: Verify syntax with bash -n**
Run: `bash -n monitor/metrics-top/background.sh monitor/metrics-top/step*/verify.sh`
Expected: 0 errors

- [ ] **Step 5: Commit**
```bash
git add tools/gen_monitor.py monitor/metrics-top/
git commit -m "feat(monitor): add Lab 1 metrics-top (Lesson 3.1)"
```

---

### Task 3: Implement Lab 2 (`app-logs`) in `tools/gen_monitor.py`

**Files:**
- Modify: `tools/gen_monitor.py`
- Output directory: `monitor/app-logs/`

**Interfaces:**
- Consumes: `labkit.lab()`, `labkit.cmd()`, `labkit.D()`
- Produces: Scenario `monitor/app-logs` with 3 steps

- [ ] **Step 1: Add Lab 2 specification to `tools/gen_monitor.py`**
Configure scenario `app-logs` for lesson 3.2:
- Setup: Pod `messenger` (two containers: `announcer` and `radio`), Pod `scout` (crashing due to `PRESSURE=20`).
- Step 1: Read second container's logs `kubectl logs messenger -c radio` -> `/root/dispatch.txt`.
- Step 2: Diagnose `scout` crash with `kubectl logs scout --previous` -> `/root/crash-error.txt`.
- Step 3: Fix `scout` so `PRESSURE=100` and it stays `Running`.

- [ ] **Step 2: Run generator**
Run: `python tools/gen_monitor.py`
Expected: `ok` printed, `monitor/app-logs/` created.

- [ ] **Step 3: Verify bash syntax**
Run: `bash -n monitor/app-logs/background.sh monitor/app-logs/step*/verify.sh`
Expected: 0 errors

- [ ] **Step 4: Commit**
```bash
git add tools/gen_monitor.py monitor/app-logs/
git commit -m "feat(monitor): add Lab 2 app-logs (Lesson 3.2)"
```

---

### Task 4: Implement Lab 3 Boss (`night-watch`) and Course Structure

**Files:**
- Modify: `tools/gen_monitor.py`
- Output directory: `monitor/night-watch/`
- Output file: `monitor/structure.json`

**Interfaces:**
- Consumes: `labkit.structure(MONITOR, ["metrics-top", "app-logs", "night-watch"])`
- Produces: `monitor/night-watch` scenario and `monitor/structure.json`

- [ ] **Step 1: Add Lab 3 Boss specification to `tools/gen_monitor.py`**
Configure scenario `night-watch` for review 3.R:
- Setup: Misconfigured `metrics-server` (scrape failure), Deployment `overdrive` in `machinery` (3 replicas, high CPU), Pod `siren` (crash-looping due to missing `PORT`).
- Step 1: Fix `metrics-server` deployment args (`--kubelet-insecure-tls`) until `kubectl top nodes` works.
- Step 2: Use `top pods` to identify `overdrive`, scale to 1 replica, and add CPU limit `200m`.
- Step 3: Check `siren`'s previous log, provide missing `PORT=8080`, and achieve `Running` phase.
- Conclude file with `labkit.structure(MONITOR, ["metrics-top", "app-logs", "night-watch"])`.

- [ ] **Step 2: Run generator**
Run: `python tools/gen_monitor.py`
Expected: `ok` printed, `monitor/night-watch/` and `monitor/structure.json` generated.

- [ ] **Step 3: Verify bash syntax and JSON**
Run: `bash -n monitor/night-watch/background.sh monitor/night-watch/step*/verify.sh`
Run: `python -c "import json; json.load(open('monitor/structure.json'))"`
Expected: 0 errors

- [ ] **Step 4: Commit**
```bash
git add tools/gen_monitor.py monitor/night-watch/ monitor/structure.json
git commit -m "feat(monitor): add Lab 3 night-watch boss (Lesson 3.R)"
```

---

### Task 5: Update Documentation and Skill References

**Files:**
- Modify: `labs.json`
- Modify: `README.md`
- Modify: `docs/GUIDE.md`
- Modify: `reels/.claude/skills/kube/references/labs.md`

**Interfaces:**
- Consumes: Lab URLs `https://killercoda.com/captainkube/course/monitor/<lab>`
- Produces: Updated mappings in `labs.json`, curriculum rows in `README.md` and `GUIDE.md`

- [ ] **Step 1: Add Module 3 mappings to `labs.json`**
Map:
- `"3.1": "https://killercoda.com/captainkube/course/monitor/metrics-top"`
- `"3.2": "https://killercoda.com/captainkube/course/monitor/app-logs"`
- `"3.R": "https://killercoda.com/captainkube/course/monitor/night-watch"`

- [ ] **Step 2: Add Module 3 table to `README.md` and summary to `docs/GUIDE.md`**
List all 3 labs with levels (`🟢`, `🟡`, `🔴`) and target lessons.

- [ ] **Step 3: Update `reels/.claude/skills/kube/references/labs.md`**
Add `tools/gen_monitor.py` to the list of generators.

- [ ] **Step 4: Commit**
```bash
git add labs.json README.md docs/GUIDE.md
git commit -m "docs: add Module 3 Logging & Monitoring lab links and documentation"
cd ../reels && git add .claude/skills/kube/references/labs.md && git commit -m "labs.md: add Module 3 generator reference [skip render]"
```

---

### Task 6: Full Validation, Git Push & Website Link Sync

**Files:**
- Repository: `captain-kube-labs` and `reels`
- Tool: `reels/.claude/skills/kube/scripts/lab_links.py`

- [ ] **Step 1: Validate all scripts across the entire labs repo**
Run `bash -n` across all `.sh` files and validate all `.json` files.
Expected: 0 errors.

- [ ] **Step 2: Push changes to GitHub for `captain-kube-labs` and `reels`**
Run `git push` on both repositories to trigger the Killercoda webhook sync.

- [ ] **Step 3: Run `lab_links.py` dry run**
Run: `python lab_links.py --dry-run`
Expected: 3 lessons (`3.1`, `3.2`, `3.R`) updated to new monitor lab URLs.

- [ ] **Step 4: Execute `lab_links.py` live**
Run: `python lab_links.py`
Expected: 3 lessons updated in Supabase, 45 total lessons with a lab.
