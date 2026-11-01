"""Generate the Captain Kube Module 2 (Scheduling) lab pack for Killercoda."""
import os, textwrap

import labkit
from labkit import ROOT, SITE, cmd

SCHED = os.path.join(ROOT, "scheduling")

NODE_READY = "kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null\n"
# so pods without placement rules can use both nodes (Killercoda may keep the control-plane taint)
UNTAINT_CP = "kubectl taint nodes controlplane node-role.kubernetes.io/control-plane:NoSchedule- >/dev/null 2>&1 || true\n"
ONE, TWO = "kubernetes-kubeadm-1node", "kubernetes-kubeadm-2nodes"


def lab(folder, title, description, intro, steps, finish, background, image=TWO):
    labkit.lab(SCHED, folder, title, description, intro, steps, finish,
               NODE_READY + textwrap.dedent(background).lstrip("\n"), image=image)


def L(code, name):
    return f"[{code} {name}]({SITE}{code})"


def done(text, next_lab=None):
    tail = f"\n\nNext lab: **{next_lab}** ⚓" if next_lab else ""
    return f"# ⚓ Well done, Captain!\n\n{labkit.D(text)}{tail}\n"


def yaml_cmd(path, body, after=""):
    """Solution block that writes a YAML file with a heredoc and applies it."""
    return (f"```plain\ncat > {path} <<'EOF'\n{textwrap.dedent(body).strip()}\nEOF\n"
            f"kubectl apply -f {path}{after}\n```{{{{exec}}}}")


ON_NODE01 = """[ "$(kubectl get pod {p} -o jsonpath='{{.spec.nodeName}}')" = "node01" ] || exit 1
[ "$(kubectl get pod {p} -o jsonpath='{{.status.phase}}')" = "Running" ] || exit 1
"""


def all_on(deploy, node="node01", ns="default"):
    return f"""[ "$(kubectl -n {ns} get deploy {deploy} -o jsonpath='{{.status.readyReplicas}}')" = "$(kubectl -n {ns} get deploy {deploy} -o jsonpath='{{.spec.replicas}}')" ] || exit 1
nodes=$(kubectl -n {ns} get pods -l app={deploy} --field-selector=status.phase=Running -o jsonpath='{{range .items[*]}}{{.spec.nodeName}}{{"\\n"}}{{end}}' | sort -u)
[ "$nodes" = "{node}" ] || exit 1
"""


# 1 · manual scheduling (2.1) ------------------------------------------------------
lab(
    "manual-scheduling",
    "🟢 Sched 1 · No harbor pilot",
    "Find why pods stay Pending, place one by hand with nodeName and bring the scheduler back.",
    f"""
    # No harbor pilot

    The **scheduler** is the harbor pilot: it decides which dock every new ship goes to.
    This morning the pilot didn't show up, and the ships are waiting outside the harbor. ⚓

    Lesson: {L("2.1", "Manual scheduling")}
    """,
    [
        dict(
            title="Why is the cargo waiting?",
            text="""
            # Why is the cargo waiting?

            The pod **`cargo`** is stuck in `Pending`. Look at the control plane and find which component is missing.

            Write its name into **`/root/missing.txt`**.
            """,
            hint="`kubectl describe pod cargo` shows no scheduling events at all. "
                 "Compare `kubectl get pods -n kube-system` with the four control-plane components.",
            solution=cmd("kubectl get pod cargo\nkubectl get pods -n kube-system") + "\n\n" + cmd("echo kube-scheduler > /root/missing.txt"),
            verify="""
            got=$(tr -d '[:space:]' < /root/missing.txt 2>/dev/null | tr 'A-Z' 'a-z')
            [ "$got" = "kube-scheduler" ] || [ "$got" = "scheduler" ] || exit 1
            """,
        ),
        dict(
            title="Pilot it yourself",
            text="""
            # Pilot it yourself

            No scheduler? Then you are the pilot. Get the pod **`cargo`** (image `nginx:1.27`) **running on `node01`**,
            without bringing the scheduler back yet.
            """,
            hint="A pod's `spec.nodeName` skips the scheduler completely, but it can only be set when the pod is created. "
                 "Delete `cargo` and create it again with `nodeName: node01`.",
            solution=cmd("kubectl delete pod cargo --now\n"
                         "kubectl run cargo --image=nginx:1.27 --overrides='{\"spec\":{\"nodeName\":\"node01\"}}'\n"
                         "kubectl get pod cargo -o wide"),
            verify=ON_NODE01.format(p="cargo") + """
            [ "$(kubectl get pod cargo -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
            """,
        ),
        dict(
            title="Call the pilot back",
            text="""
            # Call the pilot back

            Someone moved the scheduler's static pod manifest out of the manifests folder.
            Find it somewhere under `/etc/kubernetes` and **put it back**, so the scheduler pod runs again.
            """,
            hint="`find /etc/kubernetes -name '*scheduler*'`. The kubelet starts static pods from `/etc/kubernetes/manifests`.",
            solution=cmd("find /etc/kubernetes -name '*scheduler*.yaml'") + "\n\n" +
            cmd("mv /etc/kubernetes/parked/kube-scheduler.yaml /etc/kubernetes/manifests/\n"
                "kubectl get pods -n kube-system -l component=kube-scheduler -w"),
            verify="""
            [ -f /etc/kubernetes/manifests/kube-scheduler.yaml ] || exit 1
            [ "$(kubectl -n kube-system get pods -l component=kube-scheduler -o jsonpath='{.items[0].status.containerStatuses[0].ready}')" = "true" ] || exit 1
            """,
        ),
    ],
    done("""
    * No scheduler = new pods stay `Pending` with no events.
    * `spec.nodeName` places a pod directly on a node (only at creation). The scheduler itself does it with a **Binding** object.
    * The scheduler is a static pod: its manifest lives in `/etc/kubernetes/manifests`.
    """, "Sched 2 · Find ships by their flags (labels)"),
    """
    mkdir -p /etc/kubernetes/parked
    mv /etc/kubernetes/manifests/kube-scheduler.yaml /etc/kubernetes/parked/
    for i in $(seq 60); do
      [ -z "$(kubectl -n kube-system get pods -l component=kube-scheduler -o name 2>/dev/null)" ] && break
      sleep 2
    done
    kubectl run cargo --image=nginx:1.27 >/dev/null
    """,
)

# 2 · labels & selectors (2.2) -----------------------------------------------------
PODS = [("radar-1", "prod", "frontend", "red"), ("radar-2", "prod", "backend", "red"),
        ("radar-3", "prod", "frontend", "blue"), ("sonar-1", "dev", "frontend", "blue"),
        ("sonar-2", "dev", "backend", "red"), ("sonar-3", "staging", "frontend", "red"),
        ("mast-1", "staging", "backend", "blue"), ("mast-2", "prod", "backend", "blue")]
LABEL_SETUP = "".join(f"kubectl run {n} --image=registry.k8s.io/pause:3.10 --labels=env={e},tier={t},team={m} >/dev/null\n"
                      for n, e, t, m in PODS)
LABEL_SETUP += "kubectl run mast-3 --image=registry.k8s.io/pause:3.10 --labels=tier=frontend,team=red >/dev/null\n"

lab(
    "labels-selectors",
    "🟢 Sched 2 · Find ships by their flags",
    "Filter pods with equality and set-based selectors and fix a Service that selects too much.",
    f"""
    # Find ships by their flags

    Every ship flies flags: **labels**. Kubernetes finds things by flags, never by name:
    Services, ReplicaSets and Deployments all use **selectors**.

    Nine pods are in the harbor with labels `env`, `tier` and `team`.

    Lesson: {L("2.2", "Labels & selectors")}
    """,
    [
        dict(
            title="Count the prod frontends",
            text="""
            # Count the prod frontends

            How many pods have **`env=prod`** **and** **`tier=frontend`**?
            Write the number into **`/root/prod-frontend.txt`**.
            """,
            hint="`kubectl get pods -l key=value,key2=value2` (a comma means AND). `--show-labels` shows all labels.",
            solution=cmd("kubectl get pods --show-labels\nkubectl get pods -l env=prod,tier=frontend") + "\n\n" +
            cmd("kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l > /root/prod-frontend.txt"),
            verify="""
            want=$(kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l)
            [ "$(tr -d '[:space:]' < /root/prod-frontend.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="Set-based selectors",
            text="""
            # Set-based selectors

            Find the pods whose **`env` is `prod` or `staging`**, but whose **team is not `red`**.
            Write their **names**, one per line, into **`/root/selected.txt`**.
            """,
            hint="Set-based syntax: `-l 'env in (prod,staging),team!=red'`. `-o name` or `-o custom-columns=:metadata.name` prints names.",
            solution=cmd("kubectl get pods -l 'env in (prod,staging),team!=red' -o custom-columns=:metadata.name --no-headers > /root/selected.txt\ncat /root/selected.txt"),
            verify="""
            want=$(kubectl get pods -l 'env in (prod,staging),team!=red' -o custom-columns=:metadata.name --no-headers | sort)
            got=$(sed 's#^pod/##; s/[[:space:]]//g' /root/selected.txt 2>/dev/null | grep . | sort)
            [ -n "$want" ] && [ "$got" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="The Service catches too much",
            text="""
            # The Service catches too much 🔧

            The Service **`radar`** should only send traffic to **prod frontend** pods.
            Right now it also sends traffic to dev and staging pods. Fix it.

            ⚠️ Fix the Service you have: don't delete it, and don't change the pods' labels.
            """,
            hint="`kubectl describe svc radar` shows its selector and endpoints. A selector with two labels matches only pods "
                 "that have **both**. `kubectl edit svc radar` or `kubectl set selector svc radar …`.",
            solution=cmd("kubectl describe svc radar") + "\n\n" + cmd("kubectl set selector svc radar env=prod,tier=frontend\nkubectl describe svc radar | grep -i endpoints"),
            verify="""
            [ "$(kubectl get svc radar -o jsonpath='{.metadata.uid}')" = "$(cat /root/.radar-uid)" ] || exit 1
            [ "$(kubectl get svc radar -o jsonpath='{.spec.selector.env}')" = "prod" ] || exit 1
            [ "$(kubectl get svc radar -o jsonpath='{.spec.selector.tier}')" = "frontend" ] || exit 1
            [ "$(kubectl get pods -l env=prod,tier=frontend --no-headers | wc -l)" = "2" ] || exit 1
            n=$(kubectl get endpointslices -l kubernetes.io/service-name=radar -o jsonpath='{range .items[*].endpoints[*]}{.addresses[0]}{"\\n"}{end}' | grep -c .)
            [ "$n" = "2" ] || exit 1
            """,
        ),
    ],
    done("""
    * `-l a=b,c=d` means AND; `in (x,y)`, `notin`, `!=` and `key` / `!key` are the set-based forms.
    * Services, ReplicaSets and Deployments find pods only by selector: a too-wide selector sends traffic to the wrong pods.
    * Labels are for selecting; annotations are for notes that nothing selects on.
    """, "Sched 3 · Hazard flags (taints & tolerations)"),
    LABEL_SETUP + """
    kubectl create service clusterip radar --tcp=80:80 >/dev/null
    kubectl set selector svc radar tier=frontend >/dev/null
    kubectl get svc radar -o jsonpath='{.metadata.uid}' > /root/.radar-uid
    kubectl wait --for=condition=Ready pod --all --timeout=300s >/dev/null
    """,
    image=ONE,
)

# 3 · taints & tolerations (2.3) ---------------------------------------------------
lab(
    "taints-tolerations",
    "🟡 Sched 3 · Hazard flags",
    "Taint a node, write tolerations, fix a pod with a wrong toleration and see NoExecute evict pods.",
    f"""
    # Hazard flags

    A **taint** is a hazard flag on a dock: "only ships with the right papers may moor here".
    A **toleration** is those papers, carried by the pod.
    Important: papers let a ship in, they don't **send** it there.

    Two nodes: **`controlplane`** and **`node01`**. A pod **`drifter`** already runs on node01.

    Lesson: {L("2.3", "Taints & tolerations")}
    """,
    [
        dict(
            title="Raise the hazard flag",
            text="""
            # Raise the hazard flag

            Taint **`node01`** with key **`cargo`**, value **`hazardous`** and effect **`NoSchedule`**.
            """,
            hint="`kubectl taint nodes <node> key=value:Effect`",
            solution=cmd("kubectl taint nodes node01 cargo=hazardous:NoSchedule\nkubectl describe node node01 | grep -i taints"),
            verify="""
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\\n"}{end}' | grep -qx 'cargo=hazardous:NoSchedule' || exit 1
            """,
        ),
        dict(
            title="A tanker with papers",
            text="""
            # A tanker with papers

            Create a pod **`tanker`** (image `nginx:1.27`) that **tolerates** the taint and **runs on `node01`**.

            Remember: the toleration alone doesn't send it to node01. Use `nodeSelector` with the label
            `kubernetes.io/hostname: node01` to pin it.
            """,
            hint="Generate a pod with `kubectl run tanker --image=nginx:1.27 --dry-run=client -o yaml`, then add "
                 "`tolerations:` (key, operator Equal, value, effect) and `nodeSelector:` under `spec`.",
            solution=yaml_cmd("/root/tanker.yaml", """
            apiVersion: v1
            kind: Pod
            metadata:
              name: tanker
            spec:
              nodeSelector:
                kubernetes.io/hostname: node01
              tolerations:
              - key: cargo
                operator: Equal
                value: hazardous
                effect: NoSchedule
              containers:
              - name: nginx
                image: nginx:1.27
            """, "\nkubectl get pod tanker -o wide"),
            verify=ON_NODE01.format(p="tanker") + """
            kubectl get pod tanker -o jsonpath='{.spec.tolerations[*].key}' | grep -qw cargo || exit 1
            """,
        ),
        dict(
            title="The barge can't moor",
            background="""
            sleep 2
            cat <<'EOF' | kubectl apply -f - >/dev/null
            apiVersion: v1
            kind: Pod
            metadata:
              name: barge
            spec:
              nodeSelector:
                kubernetes.io/hostname: node01
              tolerations:
              - key: cargo
                operator: Equal
                value: hazardus
                effect: NoSchedule
              containers:
              - name: nginx
                image: nginx:1.27
            EOF
            """,
            text="""
            # The barge can't moor 🔧

            A new pod **`barge`** just arrived for node01 and is stuck in `Pending`.
            Find out why and get it **running on node01**.

            ⚠️ Keep node01's taint as it is: fix the barge.
            """,
            hint="`kubectl describe pod barge` → Events say which taint it doesn't tolerate. Compare its toleration with the taint, "
                 "letter by letter. Tolerations of an existing pod can't be changed: export it, fix it, recreate it.",
            solution=cmd("kubectl describe pod barge | tail -4\nkubectl get pod barge -o yaml > /root/barge.yaml") + "\n\n" +
            cmd("sed -i 's/value: hazardus/value: hazardous/' /root/barge.yaml\nkubectl replace --force -f /root/barge.yaml\nkubectl get pod barge -o wide"),
            verify="""
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\\n"}{end}' | grep -qx 'cargo=hazardous:NoSchedule' || exit 1
            """ + ON_NODE01.format(p="barge"),
        ),
        dict(
            title="The storm (NoExecute)",
            text="""
            # The storm 🌪️

            `NoSchedule` only stops **new** pods. Look: `drifter` still runs on node01 without any toleration.

            Add a second taint to node01: key **`storm`**, value **`true`**, effect **`NoExecute`**,
            and watch what happens to the pods on node01.
            """,
            hint="Same `kubectl taint` command, different effect. Then `kubectl get pods -o wide -w`.",
            solution=cmd("kubectl get pods -o wide\nkubectl taint nodes node01 storm=true:NoExecute\nkubectl get pods -o wide -w"),
            verify="""
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\\n"}{end}' | grep -qx 'storm=true:NoExecute' || exit 1
            kubectl get pod drifter >/dev/null 2>&1 && exit 1
            exit 0
            """,
        ),
    ],
    done("""
    * **NoSchedule**: no new pods without a toleration. **PreferNoSchedule**: avoid if possible.
      **NoExecute**: also **evicts** running pods that don't tolerate it.
    * A toleration lets a pod **onto** a tainted node; it doesn't attract it. To send a pod somewhere, use a nodeSelector or node affinity.
    * The control-plane node is usually tainted `node-role.kubernetes.io/control-plane:NoSchedule`.
    """, "Sched 4 · Pick the right dock (nodeSelector & affinity)"),
    """
    kubectl run drifter --image=nginx:1.27 --overrides='{"spec":{"nodeName":"node01"}}' >/dev/null
    kubectl wait --for=condition=Ready pod/drifter --timeout=300s >/dev/null
    """,
)

# 4 · nodeSelector & affinity (2.4, 2.5) -----------------------------------------
lab(
    "node-selection",
    "🟡 Sched 4 · Pick the right dock",
    "Pin pods with nodeSelector, write required node affinity and fix an affinity that matches nothing.",
    f"""
    # Pick the right dock

    Some ships need a special dock: deep water, a big crane, fast disks.
    You **label the nodes**, then the pods ask for those labels with a **nodeSelector** or **node affinity**.

    Lessons: {L("2.4", "nodeSelector")} · {L("2.5", "Node affinity")}
    """,
    [
        dict(
            title="The fast lane",
            text="""
            # The fast lane

            1. Label **`node01`** with **`disk=ssd`**
            2. Create a pod **`fastlane`** (image `nginx:1.27`) that may only run on nodes with **`disk=ssd`**, using a **nodeSelector**
            """,
            hint="`kubectl label nodes node01 disk=ssd`. In the pod: `spec.nodeSelector: {disk: ssd}`.",
            solution=cmd("kubectl label nodes node01 disk=ssd") + "\n\n" + yaml_cmd("/root/fastlane.yaml", """
            apiVersion: v1
            kind: Pod
            metadata:
              name: fastlane
            spec:
              nodeSelector:
                disk: ssd
              containers:
              - name: nginx
                image: nginx:1.27
            """),
            verify="""
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.disk}')" = "ssd" ] || exit 1
            [ "$(kubectl get pod fastlane -o jsonpath='{.spec.nodeSelector.disk}')" = "ssd" ] || exit 1
            """ + ON_NODE01.format(p="fastlane"),
        ),
        dict(
            title="East or west",
            text="""
            # East or west

            1. Label **`node01`** with **`zone=east`**
            2. Create a Deployment **`analytics`** (image `nginx:1.27`, **2 replicas**) whose pods **must** run on nodes where
               **`zone` is `east` or `west`**, using **required node affinity** with the `In` operator.
            """,
            hint="`spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[]."
                 "matchExpressions[]` with `key: zone`, `operator: In`, `values: [east, west]`. "
                 "`kubectl explain deployment.spec.template.spec.affinity.nodeAffinity` helps.",
            solution=cmd("kubectl label nodes node01 zone=east") + "\n\n" + yaml_cmd("/root/analytics.yaml", """
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: analytics
            spec:
              replicas: 2
              selector:
                matchLabels: {app: analytics}
              template:
                metadata:
                  labels: {app: analytics}
                spec:
                  affinity:
                    nodeAffinity:
                      requiredDuringSchedulingIgnoredDuringExecution:
                        nodeSelectorTerms:
                        - matchExpressions:
                          - key: zone
                            operator: In
                            values: [east, west]
                  containers:
                  - name: nginx
                    image: nginx:1.27
            """),
            verify="""
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.zone}')" = "east" ] || exit 1
            a=$(kubectl get deploy analytics -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0]}')
            echo "$a" | grep -q '"key":"zone"' || exit 1
            echo "$a" | grep -q '"operator":"In"' || exit 1
            echo "$a" | grep -q 'east' && echo "$a" | grep -q 'west' || exit 1
            """ + all_on("analytics"),
        ),
        dict(
            title="The reports never sail",
            background="""
            sleep 2
            kubectl label nodes node01 size=large --overwrite >/dev/null
            cat <<'EOF' | kubectl apply -f - >/dev/null
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: reports
            spec:
              replicas: 2
              selector:
                matchLabels: {app: reports}
              template:
                metadata:
                  labels: {app: reports}
                spec:
                  affinity:
                    nodeAffinity:
                      requiredDuringSchedulingIgnoredDuringExecution:
                        nodeSelectorTerms:
                        - matchExpressions:
                          - key: size
                            operator: In
                            values: [Large]
                  containers:
                  - name: nginx
                    image: nginx:1.27
            EOF
            """,
            text="""
            # The reports never sail 🔧

            The Deployment **`reports`** should run on the **large** node (node01), but its pods stay `Pending`.
            Fix the Deployment so both pods run on node01.

            ⚠️ Don't change the node labels: fix the Deployment.
            """,
            hint="`kubectl describe pod -l app=reports` → \"didn't match Pod's node affinity\". Compare the affinity "
                 "(`kubectl get deploy reports -o yaml`) with `kubectl get node node01 --show-labels`. Labels are case-sensitive.",
            solution=cmd("kubectl get node node01 --show-labels | tr ',' '\\n' | grep size\nkubectl get deploy reports -o yaml | grep -A3 'key: size'") + "\n\n" +
            cmd("kubectl patch deploy reports --type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/affinity/nodeAffinity/"
                "requiredDuringSchedulingIgnoredDuringExecution/nodeSelectorTerms/0/matchExpressions/0/values\",\"value\":[\"large\"]}]'\n"
                "kubectl get pods -l app=reports -o wide"),
            verify="""
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.size}')" = "large" ] || exit 1
            kubectl get deploy reports -o jsonpath='{.spec.template.spec.affinity.nodeAffinity}' | grep -q '"key":"size"' || exit 1
            """ + all_on("reports"),
        ),
    ],
    done("""
    * **nodeSelector**: simple `key: value` matching.
    * **Node affinity**: `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt`, as **required…** (hard rule) or **preferred…** (wish).
    * *IgnoredDuringExecution*: changing node labels later doesn't move running pods.
    * Labels and values are **case-sensitive**: `Large` ≠ `large`.
    """, "Sched 5 · A dock for team gold"),
    UNTAINT_CP,
)

# 5 · taints + affinity (2.6) ---------------------------------------------------------
GOLD_YAML = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gold-app
spec:
  replicas: 3
  selector:
    matchLabels: {app: gold-app}
  template:
    metadata:
      labels: {app: gold-app}
    spec:
      tolerations:
      - key: team
        operator: Equal
        value: gold
        effect: NoSchedule
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: team
                operator: In
                values: [gold]
      containers:
      - name: nginx
        image: nginx:1.27
"""

lab(
    "dedicated-nodes",
    "🟡 Sched 5 · A dock for team gold",
    "Dedicate a node to one team with a taint plus node affinity, and see why one alone isn't enough.",
    f"""
    # A dock for team gold

    Team gold bought its own dock (**node01**). Two rules:
    1. **Nobody else** may moor there.
    2. Team gold's ships may moor **only** there.

    A taint does rule 1, node affinity does rule 2. You need **both**.

    Lesson: {L("2.6", "Taints + affinity together")}
    """,
    [
        dict(
            title="Fence the dock",
            text="""
            # Fence the dock

            On **`node01`**:
            1. add the taint **`team=gold:NoSchedule`**
            2. add the label **`team=gold`**
            """,
            hint="`kubectl taint nodes …` and `kubectl label nodes …` take the same `key=value` form.",
            solution=cmd("kubectl taint nodes node01 team=gold:NoSchedule\nkubectl label nodes node01 team=gold"),
            verify="""
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\\n"}{end}' | grep -qx 'team=gold:NoSchedule' || exit 1
            [ "$(kubectl get node node01 -o jsonpath='{.metadata.labels.team}')" = "gold" ] || exit 1
            """,
        ),
        dict(
            title="Team gold sails in",
            text="""
            # Team gold sails in

            Create a Deployment **`gold-app`** (image `nginx:1.27`, **3 replicas**) whose pods:
            * **tolerate** the taint `team=gold:NoSchedule`
            * **must** run on nodes labelled `team=gold` (required node affinity)

            All 3 pods must land on node01.
            """,
            hint="Under `spec.template.spec` you need both `tolerations:` and `affinity.nodeAffinity.requiredDuring…`.",
            solution=yaml_cmd("/root/gold-app.yaml", GOLD_YAML, "\nkubectl get pods -l app=gold-app -o wide"),
            verify="""
            kubectl get deploy gold-app -o jsonpath='{.spec.template.spec.tolerations[*].key}' | grep -qw team || exit 1
            kubectl get deploy gold-app -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution}' | grep -q '"key":"team"' || exit 1
            """ + all_on("gold-app"),
        ),
        dict(
            title="The batch job strays",
            background="""
            sleep 2
            cat <<'EOF' | kubectl apply -f - >/dev/null
            apiVersion: apps/v1
            kind: Deployment
            metadata:
              name: gold-batch
            spec:
              replicas: 4
              selector:
                matchLabels: {app: gold-batch}
              template:
                metadata:
                  labels: {app: gold-batch}
                spec:
                  tolerations:
                  - key: team
                    operator: Equal
                    value: gold
                    effect: NoSchedule
                  containers:
                  - name: nginx
                    image: nginx:1.27
            EOF
            """,
            text="""
            # The batch job strays 🔧

            Team gold just deployed **`gold-batch`**. Look where its pods landed: `kubectl get pods -l app=gold-batch -o wide`.

            Some of them moor at the controlplane, outside the gold dock. Fix `gold-batch` so **all** its pods run on node01.
            """,
            hint="It has the papers (toleration) but nothing sends it to node01. Add the same required node affinity as gold-app.",
            solution=cmd("kubectl get pods -l app=gold-batch -o wide") + "\n\n" +
            cmd("kubectl patch deploy gold-batch -p '{\"spec\":{\"template\":{\"spec\":{\"affinity\":{\"nodeAffinity\":{\"requiredDuringSchedulingIgnoredDuringExecution\":"
                "{\"nodeSelectorTerms\":[{\"matchExpressions\":[{\"key\":\"team\",\"operator\":\"In\",\"values\":[\"gold\"]}]}]}}}}}}}'\n"
                "kubectl rollout status deploy/gold-batch\nkubectl get pods -l app=gold-batch -o wide"),
            verify="""
            kubectl get deploy gold-batch -o jsonpath='{.spec.template.spec.tolerations[*].key}' | grep -qw team || exit 1
            kubectl rollout status deploy/gold-batch --timeout=5s >/dev/null 2>&1 || exit 1
            """ + all_on("gold-batch"),
        ),
    ],
    done("""
    * **Taint** on the node keeps other pods **out**.
    * **Toleration** lets the team's pods **in**, but doesn't send them.
    * **Node affinity** (or nodeSelector) makes the team's pods go **only** there.
    * Dedicated nodes = taint + toleration + affinity, all three.
    """, "Sched 6 · Weigh the cargo (requests & limits)"),
    UNTAINT_CP,
)

# 6 · requests & limits (2.7) -------------------------------------------------------
lab(
    "resources",
    "🟡 Sched 6 · Weigh the cargo",
    "Set requests and limits, diagnose an OOMKilled pod and a pod too big for any node.",
    f"""
    # Weigh the cargo

    Every ship declares its cargo: **requests** are what it needs (the scheduler uses them to pick a dock),
    **limits** are the most it may ever carry. Too heavy, and the ship sinks. 🌊

    Two pods are in trouble already: **`hungry`** and **`giant`**.

    Lesson: {L("2.7", "Requests & limits")}
    """,
    [
        dict(
            title="Declare the cargo",
            text="""
            # Declare the cargo

            Create a pod **`crane`** (image `nginx:1.27`) with:
            * requests: **cpu `100m`**, **memory `64Mi`**
            * limits: **cpu `200m`**, **memory `128Mi`**
            """,
            hint="Under the container: `resources: {requests: {cpu: …, memory: …}, limits: {…}}`. "
                 "`kubectl explain pod.spec.containers.resources`.",
            solution=yaml_cmd("/root/crane.yaml", """
            apiVersion: v1
            kind: Pod
            metadata:
              name: crane
            spec:
              containers:
              - name: nginx
                image: nginx:1.27
                resources:
                  requests:
                    cpu: 100m
                    memory: 64Mi
                  limits:
                    cpu: 200m
                    memory: 128Mi
            """),
            verify="""
            r='{.spec.containers[0].resources}'
            [ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.requests.cpu}')" = "100m" ] || exit 1
            [ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.requests.memory}')" = "64Mi" ] || exit 1
            [ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.limits.cpu}')" = "200m" ] || exit 1
            [ "$(kubectl get pod crane -o jsonpath='{.spec.containers[0].resources.limits.memory}')" = "128Mi" ] || exit 1
            [ "$(kubectl get pod crane -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            """,
        ),
        dict(
            title="The hungry ship sinks",
            text="""
            # The hungry ship sinks 🔧

            The pod **`hungry`** keeps restarting. It really needs about **150 MB** of memory to do its job.

            1. Write the **reason** its container was killed into **`/root/hungry-reason.txt`** (one word, as Kubernetes shows it)
            2. Fix it so `hungry` runs **without restarting**: give it a memory limit of **256Mi**. Keep its command as it is.
            """,
            hint="`kubectl describe pod hungry` → **Last State** shows the reason. Limits of a running pod can't simply be edited: "
                 "export the YAML, change the limit, and recreate it (`kubectl replace --force -f`).",
            solution=cmd("kubectl describe pod hungry | grep -A3 'Last State'\necho OOMKilled > /root/hungry-reason.txt") + "\n\n" +
            cmd("kubectl get pod hungry -o yaml > /root/hungry.yaml\nsed -i 's/memory: 100Mi/memory: 256Mi/' /root/hungry.yaml\n"
                "kubectl replace --force -f /root/hungry.yaml\nkubectl get pod hungry -w"),
            verify="""
            [ "$(tr -d '[:space:]' < /root/hungry-reason.txt 2>/dev/null)" = "OOMKilled" ] || exit 1
            [ "$(kubectl get pod hungry -o jsonpath='{.spec.containers[0].resources.limits.memory}')" = "256Mi" ] || exit 1
            kubectl get pod hungry -o jsonpath='{.spec.containers[0].args}' | grep -q '150M' || exit 1
            [ "$(kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].restartCount}')" = "0" ] || exit 1
            kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].state.running.startedAt}' | grep -q . || exit 1
            """,
        ),
        dict(
            title="Too big for any dock",
            text="""
            # Too big for any dock 🔧

            The pod **`giant`** has been `Pending` since you arrived. Find out why and get it running.
            It must still **request** CPU (don't just delete the requests): **`250m`** is plenty.
            """,
            hint="`kubectl describe pod giant` → Events: \"Insufficient cpu\". Compare its request with "
                 "`kubectl describe node | grep -A5 Allocatable`.",
            solution=cmd("kubectl describe pod giant | tail -3\nkubectl get pod giant -o yaml > /root/giant.yaml") + "\n\n" +
            cmd("sed -i 's/cpu: \"64\"/cpu: 250m/' /root/giant.yaml\nkubectl replace --force -f /root/giant.yaml\nkubectl get pod giant"),
            verify="""
            [ "$(kubectl get pod giant -o jsonpath='{.spec.containers[0].resources.requests.cpu}')" = "250m" ] || exit 1
            [ "$(kubectl get pod giant -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            """,
        ),
    ],
    done("""
    * The scheduler places pods by **requests**; a request bigger than any node's free capacity = `Pending` ("Insufficient cpu").
    * Over the **memory limit** → the container is **OOMKilled** and restarted.
    * Over the **CPU limit** → the container is only **throttled**, never killed.
    """, "Sched 7 · Harbor rules (LimitRange & ResourceQuota)"),
    """
    cat <<'EOF' | kubectl apply -f - >/dev/null
    apiVersion: v1
    kind: Pod
    metadata:
      name: hungry
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--vm", "1", "--vm-bytes", "150M", "--vm-hang", "1"]
        resources:
          limits:
            memory: 100Mi
    ---
    apiVersion: v1
    kind: Pod
    metadata:
      name: giant
    spec:
      containers:
      - name: nginx
        image: nginx:1.27
        resources:
          requests:
            cpu: "64"
    EOF
    for i in $(seq 90); do
      [ "$(kubectl get pod hungry -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null)" -ge 1 ] 2>/dev/null && break
      sleep 2
    done
    """,
    image=ONE,
)

# 7 · LimitRange & ResourceQuota (2.8) ---------------------------------------------
lab(
    "limits-quotas",
    "🟡 Sched 7 · Harbor rules",
    "Give a namespace default requests and limits, cap it with a quota, and read quota errors.",
    f"""
    # Harbor rules

    The shipyard (namespace **`shipyard`**) gets house rules:
    * a **LimitRange** gives every container default requests and limits
    * a **ResourceQuota** caps what the whole namespace may use

    Lesson: {L("2.8", "LimitRange & ResourceQuota")}
    """,
    [
        dict(
            title="Default cargo papers",
            text="""
            # Default cargo papers

            Create a **LimitRange** **`defaults`** in namespace `shipyard` so every container that doesn't set its own gets:
            * default **requests**: cpu **`100m`**, memory **`128Mi`**
            * default **limits**: cpu **`500m`**, memory **`256Mi`**
            """,
            hint="`kind: LimitRange`, `spec.limits[]` with `type: Container`, `defaultRequest:` (requests) and `default:` (limits).",
            solution=yaml_cmd("/root/defaults.yaml", """
            apiVersion: v1
            kind: LimitRange
            metadata:
              name: defaults
              namespace: shipyard
            spec:
              limits:
              - type: Container
                defaultRequest:
                  cpu: 100m
                  memory: 128Mi
                default:
                  cpu: 500m
                  memory: 256Mi
            """, "\nkubectl -n shipyard run test --image=nginx:1.27 --dry-run=server -o yaml | grep -A6 resources"),
            verify="""
            r=$(kubectl -n shipyard run lr-check --image=nginx:1.27 --dry-run=server -o jsonpath='{.spec.containers[0].resources.requests.cpu} {.spec.containers[0].resources.requests.memory} {.spec.containers[0].resources.limits.cpu} {.spec.containers[0].resources.limits.memory}')
            [ "$r" = "100m 128Mi 500m 256Mi" ] || exit 1
            kubectl -n shipyard get limitrange defaults >/dev/null 2>&1 || exit 1
            """,
        ),
        dict(
            title="Cap the shipyard",
            text="""
            # Cap the shipyard

            Create a **ResourceQuota** **`cap`** in namespace `shipyard` with:
            * at most **5 pods**
            * total **requests.cpu `1`**
            * total **limits.memory `2Gi`**
            """,
            hint="`kubectl create quota cap -n shipyard --hard=pods=5,requests.cpu=1,limits.memory=2Gi`",
            solution=cmd("kubectl create quota cap -n shipyard --hard=pods=5,requests.cpu=1,limits.memory=2Gi\nkubectl describe quota cap -n shipyard"),
            verify="""
            h='{.spec.hard.pods} {.spec.hard.requests\\.cpu} {.spec.hard.limits\\.memory}'
            [ "$(kubectl -n shipyard get quota cap -o jsonpath="$h")" = "5 1 2Gi" ] || exit 1
            """,
        ),
        dict(
            title="The welders are short-handed",
            background="""
            sleep 2
            kubectl -n shipyard create deployment welders --image=nginx:1.27 --replicas=6 >/dev/null
            """,
            text="""
            # The welders are short-handed 🔧

            The Deployment **`welders`** in `shipyard` wants **6** pods, but fewer are running. Find out why.

            The harbor master agrees to allow **8 pods** in the shipyard. Change the quota so all 6 welders run.

            ⚠️ Keep the quota and its CPU and memory caps: only raise the pod count.
            """,
            hint="Pods that a quota refuses never appear: look at the ReplicaSet's events, "
                 "`kubectl -n shipyard describe rs -l app=welders`. Then `kubectl -n shipyard edit quota cap`.",
            solution=cmd("kubectl -n shipyard get deploy welders\nkubectl -n shipyard describe rs -l app=welders | grep -i quota | tail -2") + "\n\n" +
            cmd("kubectl -n shipyard patch quota cap -p '{\"spec\":{\"hard\":{\"pods\":\"8\"}}}'\nkubectl -n shipyard get deploy welders -w"),
            verify="""
            h='{.spec.hard.pods} {.spec.hard.requests\\.cpu} {.spec.hard.limits\\.memory}'
            [ "$(kubectl -n shipyard get quota cap -o jsonpath="$h")" = "8 1 2Gi" ] || exit 1
            [ "$(kubectl -n shipyard get deploy welders -o jsonpath='{.status.readyReplicas}')" = "6" ] || exit 1
            """,
        ),
    ],
    done("""
    * **LimitRange**: defaults (and min/max) per container, applied when the pod is created.
    * **ResourceQuota**: totals per namespace. Once a quota covers CPU or memory, every pod must declare them, and the LimitRange defaults do that for you.
    * A refused pod never exists: the reason is in the **ReplicaSet events**, not in `kubectl get pods`.
    """, "Sched 8 · Lamps on every dock (DaemonSets & static pods)"),
    """
    kubectl create namespace shipyard >/dev/null
    """,
    image=ONE,
)

# 8 · DaemonSets & static pods (2.9, 2.10) -----------------------------------------
lab(
    "daemonsets-static",
    "🟡 Sched 8 · Lamps on every dock",
    "Run one pod per node with a DaemonSet, create a static pod on a worker and remove a static pod for good.",
    f"""
    # Lamps on every dock

    Some things must run on **every** dock: a lamp, a log collector, a network agent. That's a **DaemonSet**.
    And some pods are started by the kubelet alone, from a file: **static pods**.

    Lessons: {L("2.9", "DaemonSets")} · {L("2.10", "Static pods")}
    """,
    [
        dict(
            title="A lamp on every dock",
            text="""
            # A lamp on every dock

            Create a **DaemonSet** **`lamp`** (image `busybox:1.36`, command `sleep 1d`) that runs **one pod on every node**,
            **including the controlplane**.
            """,
            hint="Start from a Deployment YAML (`kubectl create deployment lamp --image=busybox:1.36 --dry-run=client -o yaml`), "
                 "change `kind` to DaemonSet and remove `replicas` and `strategy`. Does the controlplane have a taint?",
            solution=cmd("kubectl describe node controlplane | grep -i taints") + "\n\n" + yaml_cmd("/root/lamp.yaml", """
            apiVersion: apps/v1
            kind: DaemonSet
            metadata:
              name: lamp
            spec:
              selector:
                matchLabels: {app: lamp}
              template:
                metadata:
                  labels: {app: lamp}
                spec:
                  tolerations:
                  - key: node-role.kubernetes.io/control-plane
                    operator: Exists
                    effect: NoSchedule
                  containers:
                  - name: lamp
                    image: busybox:1.36
                    command: ["sleep", "1d"]
            """, "\nkubectl get pods -l app=lamp -o wide"),
            verify="""
            n=$(kubectl get nodes --no-headers | wc -l)
            [ "$(kubectl get ds lamp -o jsonpath='{.status.desiredNumberScheduled}')" = "$n" ] || exit 1
            [ "$(kubectl get ds lamp -o jsonpath='{.status.numberReady}')" = "$n" ] || exit 1
            """,
        ),
        dict(
            title="A watchtower on node01",
            text="""
            # A watchtower on node01

            Create a **static pod** **`watchtower`** (image `nginx:1.27`) on **`node01`**.
            The kubelet on node01 must start it from a file, not the API.

            You can reach node01 with `ssh node01`.
            """,
            hint="Generate the YAML with `kubectl run watchtower --image=nginx:1.27 --dry-run=client -o yaml`, then on node01 "
                 "put it in the kubelet's `staticPodPath` (see `/var/lib/kubelet/config.yaml`). The API shows it as `watchtower-node01`.",
            solution=cmd("kubectl run watchtower --image=nginx:1.27 --dry-run=client -o yaml > /root/watchtower.yaml\n"
                         "scp /root/watchtower.yaml node01:/etc/kubernetes/manifests/\nkubectl get pods -o wide | grep watchtower"),
            verify="""
            [ "$(kubectl get pod watchtower-node01 -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            kubectl get pod watchtower-node01 -o jsonpath='{.metadata.annotations}' | grep -q 'kubernetes.io/config.mirror' || exit 1
            """,
        ),
        dict(
            title="The ghost that won't leave",
            text="""
            # The ghost that won't leave 🔧

            There's a pod called **`ghost-controlplane`** in the `default` namespace.
            Try `kubectl delete pod ghost-controlplane`, then look again. 👻

            Get rid of it **for good**.
            """,
            hint="A name ending in `-<nodename>` is a mirror pod: the kubelet recreates it from a file. "
                 "Which folder does the kubelet on the controlplane watch?",
            solution=cmd("kubectl get pod ghost-controlplane -o jsonpath='{.metadata.annotations}'; echo\n"
                         "grep -l ghost /etc/kubernetes/manifests/*") + "\n\n" +
            cmd("rm /etc/kubernetes/manifests/ghost.yaml\nkubectl get pods"),
            verify="""
            grep -lq 'name: ghost' /etc/kubernetes/manifests/* 2>/dev/null && exit 1
            kubectl get pod ghost-controlplane >/dev/null 2>&1 && exit 1
            exit 0
            """,
        ),
    ],
    done("""
    * A **DaemonSet** runs one pod per (matching) node, and adds one automatically when a node joins. It needs a toleration to run on tainted nodes.
    * **Static pods** come from files in the kubelet's `staticPodPath`; the API only shows a read-only **mirror pod** named `<pod>-<node>`.
    * Delete the file to delete a static pod.
    """, "Sched 9 · Who sails first (priority & schedulers)"),
    """
    cat > /etc/kubernetes/manifests/ghost.yaml <<'EOF'
    apiVersion: v1
    kind: Pod
    metadata:
      name: ghost
      namespace: default
    spec:
      containers:
      - name: ghost
        image: busybox:1.36
        command: ["sleep", "1d"]
    EOF
    for i in $(seq 90); do
      kubectl get pod ghost-controlplane >/dev/null 2>&1 && break
      sleep 2
    done
    """,
)

# 9 · priority & schedulers (2.11-2.13) --------------------------------------------
lab(
    "priority-schedulers",
    "🟡 Sched 9 · Who sails first",
    "Read and create PriorityClasses and fix a pod waiting for a scheduler that doesn't exist.",
    f"""
    # Who sails first

    When the harbor is full, the **PriorityClass** decides who sails first, and a high-priority pod may even push
    a lower one out (**preemption**). And every pod names its pilot: the **schedulerName**.

    Lessons: {L("2.11", "PriorityClasses")} · {L("2.12", "Multiple schedulers")} · {L("2.13", "Scheduler profiles")}
    """,
    [
        dict(
            title="Read the ranks",
            text="""
            # Read the ranks

            Kubernetes ships with built-in PriorityClasses. Write the **value** of **`system-node-critical`**
            into **`/root/node-critical.txt`**.
            """,
            hint="`kubectl get priorityclass`",
            solution=cmd("kubectl get priorityclass\nkubectl get pc system-node-critical -o jsonpath='{.value}' > /root/node-critical.txt"),
            verify="""
            [ "$(tr -d '[:space:]' < /root/node-critical.txt 2>/dev/null)" = "$(kubectl get pc system-node-critical -o jsonpath='{.value}')" ] || exit 1
            """,
        ),
        dict(
            title="The medic goes first",
            text="""
            # The medic goes first

            1. Create a PriorityClass **`critical-cargo`** with value **`1000000`** (not the global default)
            2. Create a pod **`medic`** (image `nginx:1.27`) that uses it
            """,
            hint="`kubectl create priorityclass critical-cargo --value=1000000`, then `priorityClassName:` in the pod spec.",
            solution=cmd("kubectl create priorityclass critical-cargo --value=1000000 --description='medics first'") + "\n\n" +
            yaml_cmd("/root/medic.yaml", """
            apiVersion: v1
            kind: Pod
            metadata:
              name: medic
            spec:
              priorityClassName: critical-cargo
              containers:
              - name: nginx
                image: nginx:1.27
            """),
            verify="""
            [ "$(kubectl get pc critical-cargo -o jsonpath='{.value}')" = "1000000" ] || exit 1
            [ "$(kubectl get pc critical-cargo -o jsonpath='{.globalDefault}')" != "true" ] || exit 1
            [ "$(kubectl get pod medic -o jsonpath='{.spec.priority}')" = "1000000" ] || exit 1
            [ "$(kubectl get pod medic -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            """,
        ),
        dict(
            title="Waiting for a ghost pilot",
            text="""
            # Waiting for a ghost pilot 🔧

            The pod **`parcel`** has been `Pending` forever, with no events at all. Find out why and get it running
            with the cluster's **default scheduler**.
            """,
            hint="`kubectl get pod parcel -o yaml | grep -i scheduler`. Is there a scheduler with that name in kube-system? "
                 "The field can't be changed on a running pod: recreate it.",
            solution=cmd("kubectl get pod parcel -o jsonpath='{.spec.schedulerName}'; echo\nkubectl get pods -n kube-system | grep scheduler") + "\n\n" +
            cmd("kubectl get pod parcel -o yaml > /root/parcel.yaml\nsed -i 's/schedulerName: night-pilot/schedulerName: default-scheduler/' /root/parcel.yaml\n"
                "kubectl replace --force -f /root/parcel.yaml\nkubectl get pod parcel"),
            verify="""
            [ "$(kubectl get pod parcel -o jsonpath='{.spec.schedulerName}')" = "default-scheduler" ] || exit 1
            [ "$(kubectl get pod parcel -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            """,
        ),
    ],
    done("""
    * Higher **priority** = scheduled first; when nodes are full, the scheduler may **preempt** (evict) lower-priority pods.
    * Every pod has a `schedulerName` (default `default-scheduler`). A name no scheduler answers to = `Pending` with no events.
    * One scheduler can run several **profiles**, each a set of plugins at the queue, filter, score and bind stages.
    """, "Sched 10 · The harbor gate (admission controllers)"),
    """
    cat <<'EOF' | kubectl apply -f - >/dev/null
    apiVersion: v1
    kind: Pod
    metadata:
      name: parcel
    spec:
      schedulerName: night-pilot
      containers:
      - name: nginx
        image: nginx:1.27
    EOF
    """,
    image=ONE,
)

# 10 · admission controllers (2.14, 2.15) ------------------------------------------
lab(
    "admission",
    "🟡 Sched 10 · The harbor gate",
    "Read the enabled admission plugins, enable NamespaceAutoProvision on the API server and see it work.",
    f"""
    # The harbor gate

    After the API server checks **who** you are (authentication) and **what** you may do (authorization),
    every request passes the **admission** gate: plugins that can **change** it (mutating) or **refuse** it (validating).

    You'll switch a plugin on by editing the API server's static pod manifest, like in the exam.
    ⚠️ A typo here stops the API server: make a backup first!

    Lessons: {L("2.14", "Admission controllers")} · {L("2.15", "Validating vs mutating webhooks")}
    """,
    [
        dict(
            title="Who's at the gate?",
            text="""
            # Who's at the gate?

            Find the value of the API server flag **`--enable-admission-plugins`** and write it
            (just the value, e.g. `A,B`) into **`/root/plugins.txt`**.
            """,
            hint="The flag is in `/etc/kubernetes/manifests/kube-apiserver.yaml`.",
            solution=cmd("grep enable-admission /etc/kubernetes/manifests/kube-apiserver.yaml") + "\n\n" +
            cmd("grep -o -- '--enable-admission-plugins=[^ ]*' /etc/kubernetes/manifests/kube-apiserver.yaml | cut -d= -f2 > /root/plugins.txt"),
            verify="""
            want=$(grep -o -- '--enable-admission-plugins=[^ ]*' /root/.apiserver-orig.yaml | head -1 | cut -d= -f2)
            [ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/plugins.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="Open a new gate",
            text="""
            # Open a new gate

            Enable the admission plugin **`NamespaceAutoProvision`** (keep the plugins that are already there).

            After you save the manifest, the kubelet restarts the API server: `kubectl` won't answer for up to a minute.
            Wait until `kubectl get nodes` works again.
            """,
            hint="Add `,NamespaceAutoProvision` to the end of the `--enable-admission-plugins=` value. "
                 "Back up first: `cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.bak` (never inside the manifests folder).",
            solution=cmd("cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/kube-apiserver.bak\n"
                         "sed -i 's/--enable-admission-plugins=\\(.*\\)$/--enable-admission-plugins=\\1,NamespaceAutoProvision/' /etc/kubernetes/manifests/kube-apiserver.yaml\n"
                         "grep enable-admission /etc/kubernetes/manifests/kube-apiserver.yaml") + "\n\n" +
            cmd("watch -n 3 kubectl get nodes"),
            verify="""
            grep -o -- '--enable-admission-plugins=[^ ]*' /etc/kubernetes/manifests/kube-apiserver.yaml | grep -q NamespaceAutoProvision || exit 1
            ps -o args= -C kube-apiserver | grep -q NamespaceAutoProvision || exit 1
            kubectl get --raw=/readyz >/dev/null 2>&1 || exit 1
            """,
        ),
        dict(
            title="See it work",
            text="""
            # See it work

            Without creating any namespace yourself, run a pod **`sentry`** (image `nginx:1.27`) in the namespace
            **`frontier`**, which doesn't exist yet.
            """,
            hint="`kubectl run … -n frontier`. Normally this fails with \"namespaces not found\": the new plugin creates it on the fly.",
            solution=cmd("kubectl get ns frontier\nkubectl run sentry --image=nginx:1.27 -n frontier\nkubectl get ns frontier"),
            verify="""
            kubectl get ns frontier >/dev/null 2>&1 || exit 1
            kubectl -n frontier get pod sentry >/dev/null 2>&1 || exit 1
            """,
        ),
    ],
    done("""
    * Request path: **authentication → authorization → mutating admission → validation → validating admission → etcd**.
    * Built-in plugins are switched on with `--enable-admission-plugins` on the API server.
    * Webhooks extend the same gate with your own code: **mutating first, then validating**.
    """, "Sched 11 · Nobody leaves the harbor (boss)"),
    """
    cp /etc/kubernetes/manifests/kube-apiserver.yaml /root/.apiserver-orig.yaml
    """,
    image=ONE,
)

# 11 · boss (2.R) -------------------------------------------------------------------
BOSS = """
apiVersion: apps/v1
kind: Deployment
metadata: {name: alpha, namespace: dock}
spec:
  selector: {matchLabels: {app: alpha}}
  template:
    metadata: {labels: {app: alpha}}
    spec:
      nodeSelector: {disktype: ssd}
      containers: [{name: nginx, image: "nginx:1.27"}]
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: bravo, namespace: dock}
spec:
  selector: {matchLabels: {app: bravo}}
  template:
    metadata: {labels: {app: bravo}}
    spec:
      nodeSelector: {kubernetes.io/hostname: node01}
      containers: [{name: nginx, image: "nginx:1.27"}]
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: charlie, namespace: dock}
spec:
  selector: {matchLabels: {app: charlie}}
  template:
    metadata: {labels: {app: charlie}}
    spec:
      containers:
      - name: nginx
        image: "nginx:1.27"
        resources: {requests: {cpu: "64"}}
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: delta, namespace: dock}
spec:
  selector: {matchLabels: {app: delta}}
  template:
    metadata: {labels: {app: delta}}
    spec:
      schedulerName: night-pilot
      containers: [{name: nginx, image: "nginx:1.27"}]
"""

lab(
    "pending-boss",
    "🔴 Sched 11 · Nobody leaves the harbor",
    "Boss challenge: four Deployments are stuck in Pending, each for a different scheduling reason.",
    f"""
    # Nobody leaves the harbor 🔥

    Four Deployments in namespace **`dock`** (**`alpha`**, **`bravo`**, **`charlie`**, **`delta`**) are all stuck:
    every pod is `Pending`, and **each one for a different reason**. Nobody tells you which.

    Use your Pending checklist: **scheduler → events → selectors/affinity → taints → resources → schedulerName**.

    **Rules:** keep node01's `maintenance` taint, don't delete or recreate the Deployments, and keep a CPU request on `charlie`.

    Review: {L("2.R", "Module 2 review")}
    """,
    [
        dict(
            title="Get every ship out",
            text="""
            # Get every ship out 🔥

            Goal: **`alpha`, `bravo`, `charlie` and `delta` all have their pod Running.**

            Faults hidden here: **4**.
            """,
            hint="Start with `kubectl -n dock describe pod <pod>` for each one: the **Events** name the reason "
                 "(\"didn't match node selector\", \"untolerated taint\", \"Insufficient cpu\"). One pod has **no events at all**: "
                 "who was supposed to schedule it?",
            solution="**alpha** wants a node label nobody has: label node01 (or change the selector).\n\n" +
            cmd("kubectl label nodes node01 disktype=ssd") + "\n\n**bravo** must run on node01, which has a taint: add a toleration.\n\n" +
            cmd("kubectl -n dock patch deploy bravo -p '{\"spec\":{\"template\":{\"spec\":{\"tolerations\":[{\"key\":\"maintenance\",\"operator\":\"Equal\",\"value\":\"true\",\"effect\":\"NoSchedule\"}]}}}}'") +
            "\n\n**charlie** requests 64 CPUs: ask for something sensible.\n\n" +
            cmd("kubectl -n dock set resources deploy charlie --requests=cpu=250m") +
            "\n\n**delta** waits for a scheduler that doesn't exist.\n\n" +
            cmd("kubectl -n dock patch deploy delta -p '{\"spec\":{\"template\":{\"spec\":{\"schedulerName\":\"default-scheduler\"}}}}'\nkubectl -n dock get pods -o wide"),
            verify="""
            for d in alpha bravo charlie delta; do
              [ "$(kubectl -n dock get deploy $d -o jsonpath='{.metadata.uid}')" = "$(cat /root/.uid-$d)" ] || exit 1
              [ "$(kubectl -n dock get deploy $d -o jsonpath='{.status.readyReplicas}')" = "1" ] || exit 1
            done
            kubectl get node node01 -o jsonpath='{range .spec.taints[*]}{.key}={.value}:{.effect}{"\\n"}{end}' | grep -qx 'maintenance=true:NoSchedule' || exit 1
            kubectl -n dock get deploy charlie -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}' | grep -q . || exit 1
            """,
        ),
    ],
    done("""
    You cleared four different Pending causes:

    1. **alpha**: a nodeSelector no node matched
    2. **bravo**: a tainted node without a toleration
    3. **charlie**: a CPU request bigger than any node
    4. **delta**: a schedulerName nobody answers to (no events at all!)

    Module 2 conquered. 🏆 Next on the course: [Module 3 · Logging & Monitoring](""" + SITE + """3.T)
    """),
    UNTAINT_CP +
    "kubectl taint nodes node01 maintenance=true:NoSchedule >/dev/null\n"
    "kubectl create namespace dock >/dev/null\n"
    "cat > /root/.boss.yaml <<'EOF'\n" + BOSS.strip() + "\nEOF\n"
    "kubectl apply -f /root/.boss.yaml >/dev/null && rm /root/.boss.yaml\n"
    "for d in alpha bravo charlie delta; do kubectl -n dock get deploy $d -o jsonpath='{.metadata.uid}' > /root/.uid-$d; done\n",
)

labkit.structure(SCHED, ["manual-scheduling", "labels-selectors", "taints-tolerations", "node-selection", "dedicated-nodes",
                         "resources", "limits-quotas", "daemonsets-static", "priority-schedulers", "admission", "pending-boss"])
print("ok")
