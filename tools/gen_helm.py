"""Generate the Captain Kube Helm lab pack for Killercoda."""
import os

import labkit
from labkit import ROOT, SITE, cmd

HELM = os.path.join(ROOT, "helm")


# shared pieces ---------------------------------------------------------------
INSTALL_HELM = """\
if ! command -v helm >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi
"""

MAKE_CHART = """\
mkdir -p /root/charts
cd /root/charts
helm create harbor-web >/dev/null
sed -i 's/^appVersion:.*/appVersion: "1.27"/' harbor-web/Chart.yaml
sed -i 's/^description:.*/description: The harbor web page, packed for Captain Kube/' harbor-web/Chart.yaml
cd /root
"""

def lab(folder, title, description, intro, steps, finish, background_extra=""):
    labkit.lab(HELM, folder, title, description, intro, steps, finish, INSTALL_HELM + MAKE_CHART + background_extra)


# lab 1 · first release (10.1, 10.2) ------------------------------------------
lab(
    "first-release",
    "⚓ Helm 1 · Your first release",
    "Install a chart as a named release and find what Helm created.",
    """
    # Your first release

    The harbor needs its web page back online, and the whole thing comes **packed as a Helm chart**:
    a sea chest with every Kubernetes object inside.

    The chest is waiting at `/root/charts/harbor-web`.

    In this lab you will:
    1. Install the chart as a **release** called `web`
    2. Find the objects Helm created for you

    Lessons: [10.1 Why Helm]({site}10.1) · [10.2 Charts & releases]({site}10.2)
    """.format(site=SITE),
    [
        dict(
            title="Install the release",
            text="""
            # Install the release

            Install the chart at `/root/charts/harbor-web` as a release named **`web`**
            in the namespace **`docks`**. The namespace doesn't exist yet.

            When you're done, the release must be `deployed` and its pod must be running.
            """,
            hint="`helm install <release> <chart> -n <namespace>` · there's a flag that creates the namespace for you:\n\n" +
            cmd("helm install --help | grep namespace"),
            solution=cmd("helm install web /root/charts/harbor-web -n docks --create-namespace") + "\n\n" +
            cmd("helm list -n docks\nkubectl get pods -n docks"),
            verify="""
            helm list -n docks --deployed -q | grep -qx web || exit 1
            d=$(kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
            [ -n "$d" ] || exit 1
            kubectl -n docks rollout status deploy/$d --timeout=5s >/dev/null 2>&1 || exit 1
            """,
        ),
        dict(
            title="Find what Helm created",
            text="""
            # Find what Helm created

            One `helm install` created several Kubernetes objects at once.

            Write the **name of the Deployment** that belongs to the release `web` into the file
            **`/root/deployment.txt`** (just the name, nothing else).
            """,
            hint="""
            Helm labels everything it creates with `app.kubernetes.io/instance=<release>`.
            Or ask Helm itself: `helm get manifest web -n docks`.
            """,
            solution=cmd("kubectl get deploy -n docks -l app.kubernetes.io/instance=web") + "\n\n" +
            cmd("kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}' > /root/deployment.txt"),
            verify="""
            want=$(kubectl get deploy -n docks -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
            [ -n "$want" ] || exit 1
            got=$(tr -d '[:space:]' < /root/deployment.txt 2>/dev/null)
            [ "$got" = "$want" ] || exit 1
            """,
        ),
    ],
    f"""
    # ⚓ Well done, Captain!

    You packed nothing by hand: one `helm install` unloaded a Deployment, a Service and a ServiceAccount,
    all labelled with the release name.

    Next: [10.3 Install, values, upgrade, rollback]({SITE}10.3) · then try **Helm 2 · Read the chart**.
    """,
)

# lab 2 · chart anatomy (10.2) -------------------------------------------------
lab(
    "chart-anatomy",
    "⚓ Helm 2 · Read the chart",
    "Explore Chart.yaml, values.yaml and templates, and render a chart without installing it.",
    f"""
    # Read the chart

    Before a ship leaves port, a good captain **opens the chest and checks the cargo**.

    The chart `harbor-web` is at `/root/charts/harbor-web`. You will read it and render it,
    **without installing anything** in the cluster.

    Lesson: [10.2 Charts & releases]({SITE}10.2)
    """,
    [
        dict(
            title="Read Chart.yaml and values.yaml",
            text="""
            # Read Chart.yaml and values.yaml

            Answer two questions about the chart at `/root/charts/harbor-web`:

            1. Write the chart's **version** into **`/root/chart-version.txt`**
            2. Write the default **replicaCount** into **`/root/replicas.txt`**
            """,
            hint="""
            The chart's identity card is `Chart.yaml`. The defaults live in `values.yaml`.
            Helm can show both: `helm show chart <chart>` and `helm show values <chart>`.
            """,
            solution=cmd("helm show chart /root/charts/harbor-web | grep '^version'") + "\n\n" +
            cmd("helm show values /root/charts/harbor-web | grep replicaCount") + "\n\n" +
            cmd("echo 0.1.0 > /root/chart-version.txt\necho 2 > /root/replicas.txt"),
            verify="""
            v=$(sed -n 's/^version: *//p' /root/charts/harbor-web/Chart.yaml | tr -d '"[:space:]')
            r=$(sed -n 's/^replicaCount: *//p' /root/charts/harbor-web/values.yaml | tr -d '[:space:]')
            [ "$(tr -d '[:space:]' < /root/chart-version.txt 2>/dev/null)" = "$v" ] || exit 1
            [ "$(tr -d '[:space:]' < /root/replicas.txt 2>/dev/null)" = "$r" ] || exit 1
            """,
        ),
        dict(
            title="Render without installing",
            text="""
            # Render without installing

            Render the chart with the release name **`preview`** and save the YAML to
            **`/root/rendered.yaml`**.

            ⚠️ Nothing may be installed in the cluster: no release, no new objects.
            """,
            hint="""
            There is a Helm command that only **renders** templates to YAML and never talks to the cluster.
            It takes the same release name and chart as `helm install`.
            """,
            solution=cmd("helm template preview /root/charts/harbor-web > /root/rendered.yaml") + "\n\n" +
            cmd("grep '^kind:' /root/rendered.yaml"),
            verify="""
            f=/root/rendered.yaml
            grep -q '^kind: Deployment' $f || exit 1
            grep -q '^kind: Service$' $f || exit 1
            grep -q 'preview-harbor-web' $f || exit 1
            [ -z "$(helm list -A -q)" ] || exit 1
            kubectl get deploy -A -l app.kubernetes.io/instance=preview 2>/dev/null | grep -q preview && exit 1
            exit 0
            """,
        ),
        dict(
            title="Render one template with a new value",
            text="""
            # Render one template with a new value

            The exam loves this one. Render **only the Deployment template**
            (`templates/deployment.yaml`) with **4 replicas**, release name `preview`,
            and save it to **`/root/deploy-4.yaml`**.

            The file must contain only the Deployment, nothing else.
            """,
            hint="""
            `helm template` can show a single template (`--show-only`, short `-s`)
            and accepts values with `--set key=value`.
            """,
            solution=cmd("helm template preview /root/charts/harbor-web -s templates/deployment.yaml --set replicaCount=4 > /root/deploy-4.yaml") + "\n\n" +
            cmd("grep -E '^kind|replicas' /root/deploy-4.yaml"),
            verify="""
            f=/root/deploy-4.yaml
            grep -q '^kind: Deployment' $f || exit 1
            [ "$(grep -c '^kind:' $f)" = "1" ] || exit 1
            grep -qE '^  replicas: 4$' $f || exit 1
            [ -z "$(helm list -A -q)" ] || exit 1
            """,
        ),
    ],
    f"""
    # ⚓ Well done, Captain!

    You can read a chart like a cargo list: `Chart.yaml` says what it is, `values.yaml` holds the defaults,
    `templates/` turns them into YAML, and `helm template` shows the result **without touching the cluster**.

    Next: [10.3 Install, values, upgrade, rollback]({SITE}10.3) · then try **Helm 3 · Values that win**.
    """,
    background_extra="sed -i 's/^replicaCount:.*/replicaCount: 2/' /root/charts/harbor-web/values.yaml\n",
)

# lab 3 · values precedence (10.3) --------------------------------------------
PROD_VALUES = """\
cat > /root/prod-values.yaml <<'EOF'
replicaCount: 2
podLabels:
  team: harbor
EOF
"""

lab(
    "values-precedence",
    "⚓ Helm 3 · Values that win",
    "Combine a values file with --set, then upgrade without losing your settings.",
    f"""
    # Values that win

    The market needs a shop, and the harbor master has written the settings in **`/root/prod-values.yaml`**.
    But the captain has the last word on the command line.

    Remember the order: **chart defaults < `-f` files < `--set`** (last one wins).

    Lesson: [10.3 Install, values, upgrade, rollback]({SITE}10.3)
    """,
    [
        dict(
            title="Install with a file and --set",
            text="""
            # Install with a file and --set

            Install `/root/charts/harbor-web` as release **`shop`** in namespace **`market`** (create it), using:

            * the values file **`/root/prod-values.yaml`**
            * and on the command line: **3 replicas** and service type **`NodePort`**

            Use Helm for every setting: no `kubectl edit` or `kubectl scale` afterwards.
            """,
            hint="""
            `-f <file>` for the file, `--set key=value` for the rest. Several values: `--set a=1,b=2`.
            Look at `values.yaml` to find the key for the service type.
            """,
            solution=cmd("helm install shop /root/charts/harbor-web -n market --create-namespace \\\n  -f /root/prod-values.yaml --set replicaCount=3,service.type=NodePort") + "\n\n" +
            cmd("kubectl get deploy,svc -n market"),
            verify="""
            helm list -n market --deployed -q | grep -qx shop || exit 1
            d=$(kubectl get deploy -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].metadata.name}')
            [ -n "$d" ] || exit 1
            [ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.replicas}')" = "3" ] || exit 1
            [ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.template.metadata.labels.team}')" = "harbor" ] || exit 1
            [ "$(kubectl get svc -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].spec.type}')" = "NodePort" ] || exit 1
            v=$(helm get values shop -n market -o yaml)
            echo "$v" | grep -qE '^replicaCount: 3$' || exit 1
            echo "$v" | grep -q 'NodePort' || exit 1
            """,
        ),
        dict(
            title="Upgrade without losing settings",
            text="""
            # Upgrade without losing settings

            It's a quiet day. Scale the shop down to **1 replica** with **`helm upgrade`**.

            ⚠️ The trap: after the upgrade the service must **still be `NodePort`** and the pods must
            **still have the label `team=harbor`**. An upgrade doesn't remember your old `--set` and `-f` by itself.
            """,
            hint="""
            Either pass the file and all the settings again, or tell Helm to reuse the last release's values
            and change only one: `--reuse-values`.
            """,
            solution=cmd("helm upgrade shop /root/charts/harbor-web -n market --reuse-values --set replicaCount=1") + "\n\n" +
            cmd("helm history shop -n market\nkubectl get deploy,svc -n market"),
            verify="""
            helm list -n market --deployed -q | grep -qx shop || exit 1
            rev=$(helm list -n market --filter '^shop$' -o yaml | sed -n 's/.*revision: *"\\{0,1\\}\\([0-9]*\\).*/\\1/p')
            [ "${rev:-0}" -ge 2 ] || exit 1
            d=$(kubectl get deploy -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].metadata.name}')
            [ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.replicas}')" = "1" ] || exit 1
            [ "$(kubectl get deploy $d -n market -o jsonpath='{.spec.template.metadata.labels.team}')" = "harbor" ] || exit 1
            [ "$(kubectl get svc -n market -l app.kubernetes.io/instance=shop -o jsonpath='{.items[0].spec.type}')" = "NodePort" ] || exit 1
            helm get values shop -n market -o yaml | grep -qE '^replicaCount: 1$' || exit 1
            """,
        ),
    ],
    f"""
    # ⚓ Well done, Captain!

    * `-f` files beat the chart defaults, and `--set` beats them all.
    * `helm upgrade` starts from the chart defaults again: pass your values again or use `--reuse-values`.

    Next: try **Helm 4 · The bad upgrade**, where you sail back in the logbook.
    """,
    background_extra=PROD_VALUES,
)

# lab 4 · bad upgrade + rollback (10.3) ---------------------------------------
BAD_UPGRADE = """\
helm install web /root/charts/harbor-web -n fleet --create-namespace --wait --timeout 5m >/dev/null
helm upgrade web /root/charts/harbor-web -n fleet --set image.tag=1.27-tpyo >/dev/null
"""

lab(
    "bad-upgrade",
    "⚓ Helm 4 · The bad upgrade",
    "Read the release history, find the last good revision and roll back.",
    f"""
    # The bad upgrade

    Someone upgraded the fleet's web page in a hurry, and now the new pod can't start.
    The ship is drifting. 🌊

    Helm keeps a **logbook** of every release revision. You will read it and **sail back to the last good position**.

    Lesson: [10.3 Install, values, upgrade, rollback]({SITE}10.3)
    """,
    [
        dict(
            title="Read the logbook",
            text="""
            # Read the logbook

            The release **`web`** lives in namespace **`fleet`**.

            1. Find out why the new pod is unhappy
            2. Write the number of the **last good revision** into **`/root/good-revision.txt`**
            """,
            hint="""
            `kubectl get pods -n fleet` shows the symptom. `helm history <release> -n <ns>` shows the revisions,
            and `helm get values <release> -n <ns> --revision N` shows what changed.
            """,
            solution=cmd("kubectl get pods -n fleet\nhelm history web -n fleet") + "\n\n" +
            cmd("helm get values web -n fleet --revision 2") + "\n\n" +
            "Revision 2 set a typo'd image tag (`1.27-tpyo`), so revision 1 is the good one:\n\n" +
            cmd("echo 1 > /root/good-revision.txt"),
            verify="""
            [ "$(tr -d '[:space:]' < /root/good-revision.txt 2>/dev/null)" = "1" ] || exit 1
            """,
        ),
        dict(
            title="Sail back",
            text="""
            # Sail back

            **Roll back** the release `web` to the last good revision.

            ⚠️ Use Helm's rollback: no `kubectl set image`, no uninstall + reinstall, no new upgrade.
            The logbook must keep every revision, and the pod must be running again.
            """,
            hint="""
            `helm rollback <release> [revision] -n <ns>`. Without a revision number it goes back one step.
            A rollback is written in the logbook as a **new** revision.
            """,
            solution=cmd("helm rollback web 1 -n fleet") + "\n\n" +
            cmd("helm history web -n fleet\nkubectl get pods -n fleet"),
            verify="""
            helm list -n fleet --deployed -q | grep -qx web || exit 1
            h=$(helm history web -n fleet --max 100)
            echo "$h" | grep -q 'Install complete' || exit 1
            echo "$h" | tail -n 1 | grep -q 'Rollback to 1' || exit 1
            helm get values web -n fleet -o yaml | grep -q 'tpyo' && exit 1
            d=$(kubectl get deploy -n fleet -l app.kubernetes.io/instance=web -o jsonpath='{.items[0].metadata.name}')
            kubectl get deploy $d -n fleet -o jsonpath='{.spec.template.spec.containers[0].image}' | grep -q 'tpyo' && exit 1
            kubectl -n fleet rollout status deploy/$d --timeout=5s >/dev/null 2>&1 || exit 1
            exit 0
            """,
        ),
    ],
    f"""
    # ⚓ Well done, Captain!

    * `helm history` is the logbook: every install, upgrade and rollback is a revision.
    * `helm rollback` restores the **objects** of an old revision and records it as a new one.
    * It doesn't restore **volume data**: back up before risky upgrades.

    That's the whole Helm module. ⚓ Next: [Module 11 · Kustomize]({SITE}11.T)
    """,
    background_extra=BAD_UPGRADE,
)

labkit.structure(HELM, ["first-release", "chart-anatomy", "values-precedence", "bad-upgrade"])
print("ok")
