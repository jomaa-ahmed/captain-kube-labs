# Module 3 (Logging & Monitoring) Labs Design

## Intent & Context
Add hands-on Killercoda labs for **Module 3 · Logging & Monitoring** of the Captain Kube course, covering:
- **3.1:** Metrics Server & `kubectl top` (`top nodes`, `top pods`, `--sort-by`, `--containers`, metrics pipeline)
- **3.2:** Application logs (`kubectl logs`, multi-container `-c`, CrashLoopBackOff `--previous`, log inspection)
- **3.R:** Module review (mixed practice & troubleshooting boss lab)

Course site: `captains-academy.site`
Killercoda creator: `killercoda.com/captainkube`
Repository: `captain-kube-labs`

---

## Approaches Considered

### Approach A · 3 Labs (1:1 with lessons + Boss challenge) — **Selected**
- **🟢 Mon 1 · Read the gauges (`metrics-top`, Lesson 3.1):** Using `kubectl top`, sorting, checking multi-container usage, and understanding the metrics pipeline.
- **🟡 Mon 2 · The paper tape (`app-logs`, Lesson 3.2):** Multi-container `-c` targeting, diagnosing CrashLoopBackOff with `--previous`, fixing crash causes.
- **🔴 Mon 3 · Night watch in the engine room (`night-watch`, Review 3.R Boss):** Fixing a broken metrics-server scraping configuration, spotting and throttling a rogue CPU consumer, and resolving a crashing service via `--previous` forensics.
- **Why chosen:** Aligns 1:1 with the course lessons, keeps scenarios under 15 minutes, provides direct links for `3.1`, `3.2`, and `3.R`, and follows the established badge and boss standard.

### Approach B · 4 Labs (Separate metrics-server admin from usage)
- Separates metrics server manifest installation from `kubectl top` queries into two distinct labs.
- **Rejected:** Lesson 3.1 is a concise 90s reel; two separate VM spin-ups would feel padded.

### Approach C · 2 Labs (Combined 3.1/3.2 + Boss)
- Combines `top` and `logs` into a single long lab, plus a boss lab.
- **Rejected:** Lessons 3.1 and 3.2 would have to share the same lab URL rather than offering targeted practice right after each reel.

---

## Detailed Lab Specifications

### 1. `metrics-top` (🟢 Mon 1 · Read the gauges)
- **Target Lessons:** 3.1
- **Cluster:** `kubernetes-kubeadm-1node`
- **Background setup:**
  - Installs and verifies `metrics-server` with `--kubelet-insecure-tls` in `kube-system`.
  - Deploys namespace `fleet`:
    - Pod `cruiser`: consumes moderate CPU/memory using `polinux/stress`.
    - Pod `skiff`: lightweight idle nginx.
    - Pod `freighter`: two containers (`engine` consuming 120Mi memory, `rudder` idle).
- **Steps:**
  - **Step 1: The busiest ship**
    - Task: Run `kubectl top pods -n fleet --sort-by=cpu`. Write the name of the highest CPU consumer to `/root/busiest-pod.txt`.
    - Verify: `/root/busiest-pod.txt` contains `cruiser`.
  - **Step 2: Read the node gauges**
    - Task: Check node usage with `kubectl top node`. Write the CPU millicores (e.g. `150m` or integer value) of `controlplane` to `/root/node-cpu.txt`.
    - Verify: Value in `/root/node-cpu.txt` matches within tolerance of actual node CPU usage.
  - **Step 3: Inside the double-hulled ship (`--containers`)**
    - Task: Inspect the containers of `freighter` with `kubectl top pod freighter -n fleet --containers`. Write the name of the container using more than 50Mi memory to `/root/heavy-container.txt`.
    - Verify: `/root/heavy-container.txt` contains `engine`.

### 2. `app-logs` (🟡 Mon 2 · The paper tape)
- **Target Lessons:** 3.2
- **Cluster:** `kubernetes-kubeadm-1node`
- **Background setup:**
  - Pod `messenger` in `default`:
    - Container 1 `announcer`: prints routine `heartbeat ping` every 3s.
    - Container 2 `radio`: prints `DISPATCH: harbor-clear-42` every 5s.
  - Pod `scout` in `default`:
    - Script runs `sleep 2; if [ "$PRESSURE" != "100" ]; then echo "FATAL: low boiler pressure" >&2; exit 1; fi; echo "Boiler nominal"; sleep 1d`.
    - Starts with `PRESSURE=20`, enters `CrashLoopBackOff`.
- **Steps:**
  - **Step 1: The second deckhand's report (`-c`)**
    - Task: `kubectl logs messenger` defaults to the first container (`announcer`). Read the logs of container `radio` using `-c radio` and save the dispatch token (`harbor-clear-42`) to `/root/dispatch.txt`.
    - Verify: `/root/dispatch.txt` matches `harbor-clear-42`.
  - **Step 2: The crash before the wipe (`--previous`)** 🔧
    - Task: `scout` keeps crashing. The fresh container log is empty or brief. Use `kubectl logs scout --previous` to find the fatal error message and write it to `/root/crash-error.txt`.
    - Verify: `/root/crash-error.txt` matches `FATAL: low boiler pressure`.
  - **Step 3: Fix the boiler** 🔧
    - Task: Update `scout` with `PRESSURE=100` so it stops crashing and stays `Running`.
    - Verify: `scout` is `Running`, restart count ceases to increase, and log shows `Boiler nominal`.

### 3. `night-watch` (🔴 Mon 3 · Night watch in the engine room — Boss)
- **Target Lessons:** 3.R
- **Cluster:** `kubernetes-kubeadm-1node`
- **Background setup:**
  - `metrics-server` Deployment in `kube-system` has `--kubelet-insecure-tls` intentionally omitted or misconfigured with `--kubelet-port=10255`, causing scraping failures and `Metrics API not available` for `kubectl top`.
  - Namespace `machinery`:
    - Deployment `overdrive`: 3 replicas of CPU stress with no resource limits, causing high load.
  - Namespace `machinery`:
    - Pod `siren`: crashes because `ENV` variable `PORT` is unset (`if [ -z "$PORT" ]; then echo "PANIC: siren port missing"; exit 1; fi`).
- **Steps:**
  - **Step 1: Bring the chalkboard back** 🔧
    - Task: `kubectl top nodes` is failing. Find why `metrics-server` in `kube-system` cannot reach the kubelet, fix its deployment arguments (add `--kubelet-insecure-tls`), and wait until `kubectl top nodes` works.
    - Verify: `kubectl top nodes` exits 0.
  - **Step 2: Cool the overdrive engines** 🔧
    - Task: Use `kubectl top pods -n machinery --sort-by=cpu` to identify the runaway deployment (`overdrive`). Scale it to `1` replica and configure a CPU limit of `200m`.
    - Verify: `overdrive` has 1 replica, `spec.template.spec.containers[0].resources.limits.cpu` equals `200m`, and pod is `Running`.
  - **Step 3: Silence the crash alarm (`siren`)** 🔧
    - Task: Pod `siren` in `machinery` is crash-looping. Inspect its crash logs with `--previous`, diagnose the missing environment variable, and fix the pod so it runs stably.
    - Verify: `siren` is `Running` with `PORT` set, no crashes.

---

## Course Integration
1. **Generator:** `captain-kube-labs/tools/gen_monitor.py`
2. **Lab kit:** Add `("monitor", "Captain Kube · Module 3 · Logging & Monitoring")` to `COURSES` in `tools/labkit.py`.
3. **Links:**
   - `"3.1": "https://killercoda.com/captainkube/course/monitor/metrics-top"`
   - `"3.2": "https://killercoda.com/captainkube/course/monitor/app-logs"`
   - `"3.R": "https://killercoda.com/captainkube/course/monitor/night-watch"`
4. **Website:** `lab_links.py` updates lessons 3.1, 3.2, 3.R in Supabase.
5. **Documentation:** Update `README.md`, `docs/GUIDE.md`, and `reels/.claude/skills/kube/references/labs.md`.
