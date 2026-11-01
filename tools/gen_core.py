"""Generate the Captain Kube Module 1 (Core Concepts) lab pack for Killercoda."""
import os, textwrap

import labkit
from labkit import ROOT, SITE, cmd

CORE = os.path.join(ROOT, "core")

NODE_READY = "kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null\n"
NGINX_OK = "grep -q 'Welcome to nginx'"


def lab(folder, title, description, intro, steps, finish, background):
    labkit.lab(CORE, folder, title, description, intro, steps, finish,
               NODE_READY + textwrap.dedent(background).lstrip("\n"))


def L(code, name):
    return f"[{code} {name}]({SITE}{code})"


def done(text, next_lab=None):
    tail = f"\n\nNext lab: **{next_lab}** ⚓" if next_lab else ""
    return f"# ⚓ Well done, Captain!\n\n{labkit.D(text)}{tail}\n"


# 1 · cluster tour (1.1, 1.5, 1.8) ---------------------------------------------
lab(
    "cluster-tour",
    "🟢 Core 1 · Tour the harbor",
    "Find the control plane, the static pods and the one piece that is not a pod.",
    f"""
    # Tour the harbor

    Every harbor has a **harbor office** (the control plane) and **docks** where the ships work (the nodes).
    Today you walk around and find where everything lives.

    Lessons: {L("1.1", "The Cluster Map")} · {L("1.5", "kube-apiserver")} · {L("1.8", "The kubelet")}
    """,
    [
        dict(
            title="Find the harbor office",
            text="""
            # Find the harbor office

            The control plane runs as pods in the namespace `kube-system`.

            1. Write the name of the **etcd pod** into **`/root/etcd-pod.txt`**
            2. Write the name of the **node** where the **kube-apiserver** pod runs into **`/root/api-node.txt`**
            """,
            hint="`kubectl get pods -n kube-system -o wide` shows every pod with its node.",
            solution=cmd("kubectl get pods -n kube-system -o wide") + "\n\n" +
            cmd("kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}' > /root/etcd-pod.txt\n"
                "kubectl get pods -n kube-system -l component=kube-apiserver -o jsonpath='{.items[0].spec.nodeName}' > /root/api-node.txt"),
            verify="""
            want=$(kubectl get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}')
            [ "$(tr -d '[:space:]' < /root/etcd-pod.txt 2>/dev/null)" = "$want" ] || exit 1
            want=$(kubectl get pods -n kube-system -l component=kube-apiserver -o jsonpath='{.items[0].spec.nodeName}')
            [ "$(tr -d '[:space:]' < /root/api-node.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="Find the static pods",
            text="""
            # Find the static pods

            Nobody created the control-plane pods with `kubectl`: the **kubelet** starts them from YAML files in a folder
            on the node. These are **static pods**.

            1. Write the **folder path** into **`/root/manifests.txt`**
            2. Write **how many manifest files** are in it into **`/root/manifests-count.txt`**
            """,
            hint="The kubelet's config file says where it looks: search it for `staticPodPath`. "
                 "The config file is `/var/lib/kubelet/config.yaml`.",
            solution=cmd("grep staticPodPath /var/lib/kubelet/config.yaml") + "\n\n" +
            cmd("ls /etc/kubernetes/manifests\necho /etc/kubernetes/manifests > /root/manifests.txt\n"
                "ls /etc/kubernetes/manifests | wc -l > /root/manifests-count.txt"),
            verify="""
            want=$(sed -n 's/^staticPodPath: *//p' /var/lib/kubelet/config.yaml | tr -d '[:space:]')
            want=${want%/}
            got=$(tr -d '[:space:]' < /root/manifests.txt 2>/dev/null); got=${got%/}
            [ -n "$want" ] && [ "$got" = "$want" ] || exit 1
            [ "$(tr -d '[:space:]' < /root/manifests-count.txt 2>/dev/null)" = "$(ls "$want" | wc -l)" ] || exit 1
            """,
        ),
        dict(
            title="Find the one that is not a pod",
            text="""
            # Find the one that is not a pod

            One node component can't be a pod: it's the captain who starts all the pods.

            1. Write its **name** into **`/root/not-a-pod.txt`**
            2. Write the path of **its config file** into **`/root/kubelet-config.txt`**
            """,
            hint="It runs as a normal Linux service. `systemctl status <name>` and `ps aux | grep <name>` "
                 "show how it was started, including a `--config=` flag.",
            solution=cmd("systemctl status kubelet --no-pager | head -5\nps aux | grep -o -- '--config=[^ ]*'") + "\n\n" +
            cmd("echo kubelet > /root/not-a-pod.txt\necho /var/lib/kubelet/config.yaml > /root/kubelet-config.txt"),
            verify="""
            [ "$(tr -d '[:space:]' < /root/not-a-pod.txt 2>/dev/null | tr 'A-Z' 'a-z')" = "kubelet" ] || exit 1
            want=$(ps -o args= -C kubelet | grep -o -- '--config=[^ ]*' | head -1 | cut -d= -f2)
            [ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/kubelet-config.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
    ],
    done("""
    * The control plane (apiserver, etcd, scheduler, controller-manager) runs as **static pods** from
      `/etc/kubernetes/manifests`.
    * The **kubelet** is a systemd service on every node: it reads that folder and starts the pods.
    * That's why kubeadm can't deploy the kubelet for you: something has to run first.
    """, "Core 2 · Talk to the engine room"),
    "",
)

# 2 · crictl (1.2 B) -----------------------------------------------------------
lab(
    "crictl-node",
    "🟢 Core 2 · Talk to the engine room",
    "Inspect pods and containers on the node with crictl, below Kubernetes.",
    f"""
    # Talk to the engine room

    `kubectl` talks to the harbor office. But on the node, the **container runtime** does the real work.
    `crictl` lets you talk to it directly, the way you debug a node when the API is down.

    A pod called **`lighthouse`** is already running.

    Lessons: {L("1.2A", "Did Kubernetes drop Docker?")} · {L("1.2B", "ctr vs nerdctl vs crictl")}
    """,
    [
        dict(
            title="Name the runtime",
            text="""
            # Name the runtime

            Write the **name of the container runtime** this node uses into **`/root/runtime.txt`**
            (just the name, no version).
            """,
            hint="`crictl version` prints `RuntimeName`. `kubectl get nodes -o wide` shows it too.",
            solution=cmd("crictl version") + "\n\n" + cmd("crictl version | awk '/RuntimeName/{print $2}' > /root/runtime.txt"),
            verify="""
            want=$(crictl version 2>/dev/null | awk '/RuntimeName/{print $2}')
            [ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/runtime.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="Find the container",
            text="""
            # Find the container

            Use `crictl` to find the **container ID** of the nginx container in pod `lighthouse`.
            Write it into **`/root/container-id.txt`** (the short 13-character ID is fine).
            """,
            hint="`crictl ps` lists containers with their pod name. `crictl ps --name nginx` or `--pod <pod-id>` filters.",
            solution=cmd("crictl pods --name lighthouse\ncrictl ps --name lighthouse") + "\n\n" +
            cmd("crictl ps --name lighthouse -q | head -1 > /root/container-id.txt"),
            verify="""
            full=$(kubectl get pod lighthouse -o jsonpath='{.status.containerStatuses[0].containerID}' | sed 's#.*://##')
            got=$(tr -d '[:space:]' < /root/container-id.txt 2>/dev/null)
            [ ${#got} -ge 12 ] || exit 1
            case "$full" in "$got"*) exit 0 ;; *) exit 1 ;; esac
            """,
        ),
        dict(
            title="Find the pod's address",
            text="""
            # Find the pod's address

            Every pod gets its own IP from its **sandbox**. Use `crictl inspectp` on the lighthouse pod sandbox
            and write the pod's **IP address** into **`/root/pod-ip.txt`**.
            """,
            hint="`crictl pods --name lighthouse -q` gives the sandbox ID; `crictl inspectp <id> | grep -i ip`.",
            solution=cmd("crictl inspectp $(crictl pods --name lighthouse -q) | grep '\"ip\"'") + "\n\n" +
            cmd("crictl inspectp $(crictl pods --name lighthouse -q) | grep -m1 '\"ip\"' | grep -oE '[0-9.]{7,}' > /root/pod-ip.txt"),
            verify="""
            want=$(kubectl get pod lighthouse -o jsonpath='{.status.podIP}')
            [ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/pod-ip.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
    ],
    done("""
    * Kubernetes talks to the runtime (here **containerd**) through the **CRI**.
    * `crictl` speaks CRI too: `crictl pods`, `crictl ps`, `crictl inspectp`, `crictl logs`.
    * Docker isn't needed on the node: images built with Docker still run, because they follow the OCI standard.
    """, "Core 3 · Open the logbook (etcd)"),
    """
    [ -f /etc/crictl.yaml ] || echo 'runtime-endpoint: unix:///run/containerd/containerd.sock' > /etc/crictl.yaml
    kubectl run lighthouse --image=nginx:1.27 >/dev/null
    kubectl wait --for=condition=Ready pod/lighthouse --timeout=300s >/dev/null
    """,
)

# 3 · etcd (1.3, 1.4) ----------------------------------------------------------
ETCDCTL = ("kubectl -n kube-system exec $(kubectl -n kube-system get pod -l component=etcd -o name) -- etcdctl \\\n"
           "  --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt \\\n"
           "  --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key")

lab(
    "etcd-peek",
    "🟡 Core 3 · Open the logbook (etcd)",
    "Find etcd's certificates, run etcdctl and read where Kubernetes stores a pod.",
    f"""
    # Open the logbook

    **etcd** is the harbor's logbook: every object you create is written there.
    You will open it with `etcdctl`, read-only. Never write to etcd by hand!

    A pod called **`lighthouse`** is running in `default`.

    Lessons: {L("1.3", "etcd: a key-value store")} · {L("1.4", "etcd inside Kubernetes")}
    """,
    [
        dict(
            title="Find the keys to the logbook",
            text="""
            # Find the keys to the logbook

            etcd only talks to clients with the right certificates. Its static pod manifest says which files it uses.

            Write the path of etcd's **trusted CA file** into **`/root/etcd-ca.txt`**.
            """,
            hint="Look in `/etc/kubernetes/manifests/etcd.yaml` for a flag with `trusted-ca` in its name.",
            solution=cmd("grep -E 'crt|key' /etc/kubernetes/manifests/etcd.yaml") + "\n\n" +
            cmd("grep -o -- '--trusted-ca-file=[^ ]*' /etc/kubernetes/manifests/etcd.yaml | cut -d= -f2 > /root/etcd-ca.txt"),
            verify="""
            want=$(grep -o -- '--trusted-ca-file=[^ ]*' /etc/kubernetes/manifests/etcd.yaml | head -1 | cut -d= -f2)
            [ -n "$want" ] && [ "$(tr -d '[:space:]' < /root/etcd-ca.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
        dict(
            title="Find the lighthouse",
            text="""
            # Find the lighthouse

            The etcd image contains `etcdctl`. Run it **inside the etcd pod** with the certificates, list the keys
            under `/registry/pods/default`, and write the **key of pod `lighthouse`** into **`/root/lighthouse-key.txt`**.
            """,
            hint="`kubectl exec -n kube-system <etcd-pod> -- etcdctl --endpoints=https://127.0.0.1:2379 "
                 "--cacert=… --cert=… --key=… get /registry/pods/default --prefix --keys-only`. "
                 "The server cert and key sit next to the CA file.",
            solution=cmd(ETCDCTL + " \\\n  get /registry/pods/default --prefix --keys-only") + "\n\n" +
            cmd("echo /registry/pods/default/lighthouse > /root/lighthouse-key.txt"),
            verify="""
            [ "$(tr -d '[:space:]' < /root/lighthouse-key.txt 2>/dev/null)" = "/registry/pods/default/lighthouse" ] || exit 1
            """,
        ),
        dict(
            title="The logbook is the truth",
            text="""
            # The logbook is the truth

            `kubectl get` just reads what etcd holds. Count the **Deployment keys** stored under
            `/registry/deployments/kube-system` with etcdctl, and write the number into **`/root/deploy-count.txt`**.

            Then compare with `kubectl get deploy -n kube-system`: same number?
            """,
            hint="Same etcdctl command as before, with the prefix `/registry/deployments/kube-system` "
                 "and `--keys-only`. Count the lines with `grep -c .`.",
            solution=cmd(ETCDCTL + " \\\n  get /registry/deployments/kube-system --prefix --keys-only | grep -c . > /root/deploy-count.txt") +
            "\n\n" + cmd("cat /root/deploy-count.txt\nkubectl get deploy -n kube-system"),
            verify="""
            want=$(kubectl get deploy -n kube-system --no-headers 2>/dev/null | wc -l)
            [ "$(tr -d '[:space:]' < /root/deploy-count.txt 2>/dev/null)" = "$want" ] || exit 1
            """,
        ),
    ],
    done("""
    * etcd stores every object under `/registry/<type>/<namespace>/<name>`.
    * It runs as a static pod, and only clients with its certificates may talk to it.
    * Backups (`etcdctl snapshot save`) are how you save the whole harbor: that comes in Module 5.
    """, "Core 4 · Launch your first pods"),
    """
    kubectl run lighthouse --image=nginx:1.27 >/dev/null
    kubectl wait --for=condition=Ready pod/lighthouse --timeout=300s >/dev/null
    """,
)

# 4 · pods (1.10, 1.11) --------------------------------------------------------
lab(
    "pods-first",
    "🟢 Core 4 · Launch your first pods",
    "Write a pod in YAML, fix a pod that can't start and build a pod with a sidecar.",
    f"""
    # Launch your first pods

    A pod is the smallest boat in the harbor: one or more containers that sail together.
    You'll write one from scratch, rescue a broken one and build one with a sidecar.

    Lessons: {L("1.10", "Pods")} · {L("1.11", "A pod in YAML")}
    """,
    [
        dict(
            title="Write a pod in YAML",
            text="""
            # Write a pod in YAML

            Write the file **`/root/lighthouse.yaml`** yourself and create the pod from it:

            * name **`lighthouse`**, image **`nginx:1.27`**
            * labels **`app=harbor`** and **`tier=front`**

            The file must have the 4 top-level fields of every Kubernetes object.
            """,
            hint="`apiVersion`, `kind`, `metadata` (name + labels), `spec` (containers: name + image). "
                 "Then `kubectl apply -f /root/lighthouse.yaml`.",
            solution="```plain\ncat > /root/lighthouse.yaml <<'EOF'\napiVersion: v1\nkind: Pod\nmetadata:\n  name: lighthouse\n"
                     "  labels:\n    app: harbor\n    tier: front\nspec:\n  containers:\n  - name: nginx\n    image: nginx:1.27\nEOF\n"
                     "kubectl apply -f /root/lighthouse.yaml\n```{{exec}}",
            verify="""
            f=/root/lighthouse.yaml
            for k in apiVersion kind metadata spec; do grep -q "^$k:" $f || exit 1; done
            [ "$(kubectl get pod lighthouse -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            [ "$(kubectl get pod lighthouse -o jsonpath='{.metadata.labels.app}')" = "harbor" ] || exit 1
            [ "$(kubectl get pod lighthouse -o jsonpath='{.metadata.labels.tier}')" = "front" ] || exit 1
            [ "$(kubectl get pod lighthouse -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
            """,
        ),
        dict(
            title="Rescue the ferry",
            text="""
            # Rescue the ferry 🔧

            The pod **`ferry`** can't start. Find out why and fix it, so `ferry` is **Running**
            with the **Alpine** variant of nginx 1.27. Keep the name `ferry`.
            """,
            hint="`kubectl get pod ferry` shows the status, `kubectl describe pod ferry` shows the events at the bottom. "
                 "A pod's image can be changed in place: `kubectl set image` or `kubectl edit`.",
            solution=cmd("kubectl describe pod ferry | tail -5") + "\n\n" +
            cmd("kubectl set image pod/ferry ferry=nginx:1.27-alpine\nkubectl get pod ferry -w"),
            verify="""
            [ "$(kubectl get pod ferry -o jsonpath='{.status.phase}')" = "Running" ] || exit 1
            [ "$(kubectl get pod ferry -o jsonpath='{.spec.containers[0].image}')" = "nginx:1.27-alpine" ] || exit 1
            """,
        ),
        dict(
            title="Add a sidecar",
            text="""
            # Add a sidecar

            Create a pod **`signal`** with **two containers**:

            * **`web`**: image `nginx:1.27`
            * **`logger`**: image `busybox:1.36`, command `sh -c 'while true; do echo ahoy; sleep 5; done'`

            Both containers must be ready, and `logger` must be printing `ahoy`.
            """,
            hint="Start from `kubectl run signal --image=nginx:1.27 --dry-run=client -o yaml > signal.yaml`, "
                 "rename the container to `web` and add a second item under `containers`.",
            solution="```plain\ncat > /root/signal.yaml <<'EOF'\napiVersion: v1\nkind: Pod\nmetadata:\n  name: signal\nspec:\n"
                     "  containers:\n  - name: web\n    image: nginx:1.27\n  - name: logger\n    image: busybox:1.36\n"
                     "    command: [\"sh\", \"-c\", \"while true; do echo ahoy; sleep 5; done\"]\nEOF\n"
                     "kubectl apply -f /root/signal.yaml\nkubectl logs signal -c logger\n```{{exec}}",
            verify="""
            [ "$(kubectl get pod signal -o jsonpath='{.spec.containers[*].name}')" = "web logger" ] || exit 1
            [ "$(kubectl get pod signal -o jsonpath='{.status.containerStatuses[*].ready}')" = "true true" ] || exit 1
            kubectl logs signal -c logger --tail=5 2>/dev/null | grep -q ahoy || exit 1
            """,
        ),
    ],
    done("""
    * Every object has `apiVersion`, `kind`, `metadata` and `spec`.
    * `kubectl describe` → **Events** tells you why a pod won't start (here: an image that doesn't exist).
    * Containers in one pod share the network and storage: a sidecar helps the main container.
    """, "Core 5 · Keep the crew complete (ReplicaSets)"),
    """
    kubectl run ferry --image=nginx:1.27-alpne >/dev/null
    """,
)

# 5 · replicasets (1.6, 1.12) --------------------------------------------------
lab(
    "replicasets",
    "🟡 Core 5 · Keep the crew complete",
    "Watch the control loop replace pods, scale a ReplicaSet and fix one with a bad image.",
    f"""
    # Keep the crew complete

    A ReplicaSet is the bosun who counts the crew: if a sailor is missing, he hires a new one.
    It finds its crew by **labels**.

    Two ReplicaSets are on deck: **`crew`** (healthy) and **`deckhands`** (something's wrong).

    Lessons: {L("1.6", "Controllers")} · {L("1.12", "ReplicaSets & labels")}
    """,
    [
        dict(
            title="Watch the control loop",
            text="""
            # Watch the control loop

            Delete **one** pod of the ReplicaSet `crew` and watch what happens.

            Write the name of the **new pod** the ReplicaSet created into **`/root/new-pod.txt`**.
            """,
            hint="`kubectl get pods -l app=crew`, delete one with `kubectl delete pod <name>`, then list again: "
                 "the youngest pod (smallest AGE) is the new one.",
            solution=cmd("kubectl delete pod $(kubectl get pods -l app=crew -o jsonpath='{.items[0].metadata.name}')") + "\n\n" +
            cmd("kubectl get pods -l app=crew --sort-by=.metadata.creationTimestamp\n"
                "kubectl get pods -l app=crew --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}' > /root/new-pod.txt"),
            verify="""
            p=$(tr -d '[:space:]' < /root/new-pod.txt 2>/dev/null)
            [ -n "$p" ] || exit 1
            [ "$(kubectl get pod "$p" -o jsonpath='{.metadata.labels.app}' 2>/dev/null)" = "crew" ] || exit 1
            # the new pod must not be one of the pods that existed when the lab started
            grep -qx "$p" /root/.crew-initial-pods && exit 1
            # and the ReplicaSet must own it (not a hand-made pod with the same label)
            [ "$(kubectl get pod "$p" -o jsonpath='{.metadata.ownerReferences[0].name}')" = "crew" ] || exit 1
            exit 0
            """,
        ),
        dict(
            title="Hire more crew",
            text="""
            # Hire more crew

            Big cargo today. Scale the ReplicaSet **`crew`** to **5** pods, all ready.
            """,
            hint="`kubectl scale rs <name> --replicas=N`, or change `replicas` with `kubectl edit rs crew`.",
            solution=cmd("kubectl scale rs crew --replicas=5\nkubectl get rs crew"),
            verify="""
            [ "$(kubectl get rs crew -o jsonpath='{.spec.replicas}')" = "5" ] || exit 1
            [ "$(kubectl get rs crew -o jsonpath='{.status.readyReplicas}')" = "5" ] || exit 1
            """,
        ),
        dict(
            title="Fix the deckhands",
            text="""
            # Fix the deckhands 🔧

            The ReplicaSet **`deckhands`** has pods that never start. Fix it so **both** pods run **`nginx:1.27`**.

            ⚠️ Don't delete or recreate the ReplicaSet itself: fix the one you have.
            """,
            hint="Fixing the image in the ReplicaSet template is only half the job: a ReplicaSet doesn't replace "
                 "pods that already exist. What happens if the old pods go away?",
            solution=cmd("kubectl describe pods -l app=deckhands | grep -A3 Events") + "\n\n" +
            cmd("kubectl set image rs/deckhands nginx=nginx:1.27\nkubectl delete pods -l app=deckhands\nkubectl get pods -l app=deckhands"),
            verify="""
            [ "$(kubectl get rs deckhands -o jsonpath='{.metadata.uid}')" = "$(cat /root/.deckhands-uid)" ] || exit 1
            [ "$(kubectl get rs deckhands -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
            imgs=$(kubectl get pods -l app=deckhands -o jsonpath='{range .items[*]}{.spec.containers[0].image} {.status.phase}{"\\n"}{end}')
            [ "$(echo "$imgs" | grep -c 'nginx:1.27 Running')" = "2" ] || exit 1
            [ "$(echo "$imgs" | grep -c .)" = "2" ] || exit 1
            """,
        ),
    ],
    done("""
    * Controllers loop forever: **watch → compare → act**. Delete a pod, and the ReplicaSet makes a new one.
    * A ReplicaSet finds its pods by **labels**, not by name.
    * Changing a ReplicaSet's template doesn't touch running pods. A **Deployment** does that for you,
      which is why we use Deployments: next lab.
    """, "Core 6 · Roll out the fleet (Deployments)"),
    """
    cat > /root/.rs.yaml <<'EOF'
    apiVersion: apps/v1
    kind: ReplicaSet
    metadata:
      name: crew
    spec:
      replicas: 3
      selector:
        matchLabels: {app: crew}
      template:
        metadata:
          labels: {app: crew}
        spec:
          containers:
          - name: nginx
            image: nginx:1.27
    ---
    apiVersion: apps/v1
    kind: ReplicaSet
    metadata:
      name: deckhands
    spec:
      replicas: 2
      selector:
        matchLabels: {app: deckhands}
      template:
        metadata:
          labels: {app: deckhands}
        spec:
          containers:
          - name: nginx
            image: nginx:1.27-tpyo
    EOF
    kubectl apply -f /root/.rs.yaml >/dev/null && rm /root/.rs.yaml
    kubectl get rs deckhands -o jsonpath='{.metadata.uid}' > /root/.deckhands-uid
    kubectl wait --for=condition=Ready pod -l app=crew --timeout=300s >/dev/null
    kubectl get pods -l app=crew -o jsonpath='{range .items[*]}{.metadata.name}{"\\n"}{end}' > /root/.crew-initial-pods
    """,
)

# 6 · deployments (1.13) -------------------------------------------------------
lab(
    "deployments",
    "🟡 Core 6 · Roll out the fleet",
    "Create a Deployment, roll out a new version and undo a broken rollout.",
    f"""
    # Roll out the fleet

    A Deployment is the fleet admiral: it manages ReplicaSets for you, swaps versions **without downtime**
    and remembers every rollout so you can go back.

    Lesson: {L("1.13", "Deployments")}
    """,
    [
        dict(
            title="Launch the fleet",
            text="""
            # Launch the fleet

            Create a Deployment **`cargo`** with image **`nginx:1.26`** and **3 replicas**.
            Use one imperative command, as you would in the exam.
            """,
            hint="`kubectl create deployment <name> --image=<image> --replicas=<n>`",
            solution=cmd("kubectl create deployment cargo --image=nginx:1.26 --replicas=3\nkubectl get deploy,rs,pods"),
            verify="""
            [ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.26" ] || exit 1
            [ "$(kubectl get deploy cargo -o jsonpath='{.status.readyReplicas}')" = "3" ] || exit 1
            kubectl get deploy cargo -o jsonpath='{.metadata.uid}' > /root/.cargo-uid
            """,
        ),
        dict(
            title="Roll out a new version",
            text="""
            # Roll out a new version

            Update `cargo` to **`nginx:1.27`** and watch the rollout replace the pods one by one.

            ⚠️ Update the Deployment you have: don't delete it.
            """,
            hint="`kubectl set image deployment/<name> <container>=<image>`. The container is called `nginx`. "
                 "Watch with `kubectl rollout status`.",
            solution=cmd("kubectl set image deployment/cargo nginx=nginx:1.27\nkubectl rollout status deployment/cargo\nkubectl get rs"),
            verify="""
            [ "$(kubectl get deploy cargo -o jsonpath='{.metadata.uid}')" = "$(cat /root/.cargo-uid 2>/dev/null)" ] || exit 1
            [ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
            kubectl rollout status deployment/cargo --timeout=5s >/dev/null 2>&1 || exit 1
            """,
        ),
        dict(
            title="Undo the bad rollout",
            background="""
            sleep 2
            kubectl set image deployment/cargo '*=nginx:1.27-broken' >/dev/null
            """,
            text="""
            # Undo the bad rollout 🔧

            Oh no: a crew member just pushed a new version of `cargo`, and the new pods won't start. 🌊
            (Look: `kubectl get pods`.)

            Find it in the rollout history and **undo** it, so all 3 pods run `nginx:1.27` again.

            ⚠️ Use the rollout history: no new `set image`, no delete and recreate.
            """,
            hint="`kubectl rollout history deployment/cargo` lists the revisions. "
                 "`kubectl rollout undo` goes back one revision (or `--to-revision=N`).",
            solution=cmd("kubectl get pods\nkubectl rollout history deployment/cargo") + "\n\n" +
            cmd("kubectl rollout undo deployment/cargo\nkubectl rollout status deployment/cargo"),
            verify="""
            [ "$(kubectl get deploy cargo -o jsonpath='{.metadata.uid}')" = "$(cat /root/.cargo-uid 2>/dev/null)" ] || exit 1
            [ "$(kubectl get deploy cargo -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ] || exit 1
            rev=$(kubectl get deploy cargo -o jsonpath='{.metadata.annotations.deployment\\.kubernetes\\.io/revision}')
            [ "${rev:-0}" -ge 4 ] || exit 1
            # the broken ReplicaSet must still exist (history kept) and be scaled to 0
            broken=$(kubectl get rs -l app=cargo -o jsonpath='{range .items[*]}{.spec.template.spec.containers[0].image} {.spec.replicas}{"\\n"}{end}' | grep '1.27-broken')
            [ -n "$broken" ] || exit 1
            echo "$broken" | grep -qv ' 0$' && exit 1
            kubectl rollout status deployment/cargo --timeout=5s >/dev/null 2>&1 || exit 1
            """,
        ),
    ],
    done("""
    * Deployment → ReplicaSet → Pods: each version gets its own ReplicaSet.
    * A rollout replaces pods step by step; `kubectl rollout undo` scales the old ReplicaSet back up.
    * Never create bare pods or bare ReplicaSets for an app: use a Deployment.
    """, "Core 7 · Give the harbor an address (Services)"),
    "",
)

# 7 · services (1.9, 1.14-1.17) ------------------------------------------------
lab(
    "services-fix",
    "🟡 Core 7 · Give the harbor an address",
    "Fix a Service with no endpoints, expose an app on a NodePort, create a ClusterIP for a backend and see why a LoadBalancer stays pending.",
    f"""
    # Give the harbor an address

    Pods come and go, and their IPs change. A **Service** is the harbor's fixed address: it finds pods by
    **labels** and sends traffic to them.

    On deck: Deployments **`web`** and **`api`**, a Service **`web`** that doesn't work, and a pod **`client`**.

    Lessons: {L("1.14", "Services")} · {L("1.15", "NodePort")} · {L("1.16", "ClusterIP")} · {L("1.17", "LoadBalancer")} · {L("1.9", "kube-proxy")}
    """,
    [
        dict(
            title="Fix the web Service",
            text="""
            # Fix the web Service 🔧

            The Service **`web`** has an address, but nothing answers. Fix it so
            `curl http://<web ClusterIP>` returns the nginx welcome page.

            ⚠️ Fix the Service you have: don't delete it or create a new one.
            There may be more than one thing wrong.
            """,
            hint="Compare the Service's **selector** with the pod labels (`kubectl get pods --show-labels`), "
                 "and its **targetPort** with the port nginx listens on. "
                 "`kubectl get endpointslices -l kubernetes.io/service-name=web` shows whether it found pods.",
            solution=cmd("kubectl describe svc web\nkubectl get pods --show-labels") + "\n\n" +
            cmd("kubectl patch svc web -p '{\"spec\":{\"selector\":{\"app\":\"web\"},\"ports\":[{\"port\":80,\"targetPort\":80}]}}'") +
            "\n\n" + cmd("curl -s http://$(kubectl get svc web -o jsonpath='{.spec.clusterIP}') | head -4"),
            verify="""
            [ "$(kubectl get svc web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.web-uid)" ] || exit 1
            ip=$(kubectl get svc web -o jsonpath='{.spec.clusterIP}')
            port=$(kubectl get svc web -o jsonpath='{.spec.ports[0].port}')
            curl -s -m 3 "http://$ip:$port" | """ + NGINX_OK + """ || exit 1
            """,
        ),
        dict(
            title="Open it to the world",
            text="""
            # Open it to the world

            Create a Service **`web-public`** of type **NodePort** for the Deployment `web`,
            on node port **30080**, so `curl http://localhost:30080` works from the node.
            """,
            hint="`kubectl expose deployment web --name=web-public --type=NodePort --port=80` creates it with a random "
                 "node port; set `nodePort: 30080` with `kubectl edit`, or write the YAML with `--dry-run=client -o yaml`.",
            solution=cmd("kubectl expose deployment web --name=web-public --type=NodePort --port=80 --dry-run=client -o yaml > /root/web-public.yaml") +
            "\n\n" + cmd("sed -i 's/^  - port: 80$/  - port: 80\\n    nodePort: 30080/' /root/web-public.yaml\n"
                         "kubectl apply -f /root/web-public.yaml\ncurl -s localhost:30080 | head -4"),
            verify="""
            [ "$(kubectl get svc web-public -o jsonpath='{.spec.type}')" = "NodePort" ] || exit 1
            [ "$(kubectl get svc web-public -o jsonpath='{.spec.ports[0].nodePort}')" = "30080" ] || exit 1
            curl -s -m 3 http://localhost:30080 | """ + NGINX_OK + """ || exit 1
            """,
        ),
        dict(
            title="An address for the backend",
            text="""
            # An address for the backend

            The pod **`client`** needs to reach the Deployment **`api`** at **`http://api`**.
            Create a **ClusterIP** Service called **`api`** on port **80** for it.

            Test: `kubectl exec client -- wget -qO- -T 3 http://api`
            """,
            hint="`kubectl expose deployment api --port=80` creates a ClusterIP Service named after the Deployment.",
            solution=cmd("kubectl expose deployment api --port=80\nkubectl exec client -- wget -qO- -T 3 http://api | head -4"),
            verify="""
            [ "$(kubectl get svc api -o jsonpath='{.spec.type}')" = "ClusterIP" ] || exit 1
            kubectl exec client -- wget -qO- -T 3 http://api 2>/dev/null | """ + NGINX_OK + """ || exit 1
            """,
        ),
        dict(
            title="Ask for a LoadBalancer",
            text="""
            # Ask for a LoadBalancer

            In the cloud, a **LoadBalancer** Service gets a public IP from the cloud provider. This harbor has no cloud.

            1. Create a Service **`web-lb`** of type **LoadBalancer** for the Deployment `web`, on port **80**
            2. Look at its **EXTERNAL-IP** column and write exactly what you see there into **`/root/lb-external.txt`**
            3. A LoadBalancer is built **on top of a NodePort**: write its node port into **`/root/lb-nodeport.txt`**
               and check that `curl http://localhost:<that port>` already works
            """,
            hint="`kubectl expose deployment web --name=web-lb --type=LoadBalancer --port=80`, then `kubectl get svc web-lb`. "
                 "The node port is in the PORT(S) column (`80:3xxxx/TCP`) or `-o jsonpath='{.spec.ports[0].nodePort}'`.",
            solution=cmd("kubectl expose deployment web --name=web-lb --type=LoadBalancer --port=80\nkubectl get svc web-lb") + "\n\n" +
            cmd("echo '<pending>' > /root/lb-external.txt\n"
                "kubectl get svc web-lb -o jsonpath='{.spec.ports[0].nodePort}' > /root/lb-nodeport.txt\n"
                "curl -s localhost:$(cat /root/lb-nodeport.txt) | head -4"),
            verify="""
            [ "$(kubectl get svc web-lb -o jsonpath='{.spec.type}')" = "LoadBalancer" ] || exit 1
            np=$(kubectl get svc web-lb -o jsonpath='{.spec.ports[0].nodePort}')
            [ -n "$np" ] || exit 1
            [ "$(tr -d '[:space:]' < /root/lb-nodeport.txt 2>/dev/null)" = "$np" ] || exit 1
            ext=$(kubectl get svc web-lb -o jsonpath='{.status.loadBalancer.ingress[0].ip}{.status.loadBalancer.ingress[0].hostname}')
            got=$(tr -d '[:space:]<>' < /root/lb-external.txt 2>/dev/null | tr 'A-Z' 'a-z')
            [ "$got" = "${ext:-pending}" ] || exit 1
            curl -s -m 3 "http://localhost:$np" | """ + NGINX_OK + """ || exit 1
            """,
        ),
    ],
    done("""
    * A Service finds pods by **selector**; no matching labels = no endpoints = nothing answers.
    * `port` is the Service's port, `targetPort` the container's, `nodePort` (30000-32767) the one on every node.
    * kube-proxy writes the rules on each node that turn the Service IP into pod IPs.
    * **LoadBalancer** stays `<pending>` without a cloud (or MetalLB) to hand out the external IP,
      but it already works as a NodePort underneath.
    """, "Core 8 · Sail between harbors (Namespaces)"),
    """
    kubectl create deployment web --image=nginx:1.27 --replicas=2 >/dev/null
    kubectl create deployment api --image=nginx:1.27 >/dev/null
    kubectl create service clusterip web --tcp=80:8080 >/dev/null
    kubectl patch svc web -p '{"spec":{"selector":{"app":"wbe"}}}' >/dev/null
    kubectl get svc web -o jsonpath='{.metadata.uid}' > /root/.web-uid
    kubectl run client --image=busybox:1.36 -- sleep 1d >/dev/null
    kubectl wait --for=condition=Available deploy/web deploy/api --timeout=300s >/dev/null
    kubectl wait --for=condition=Ready pod/client --timeout=300s >/dev/null
    """,
)

# 8 · namespaces (1.18) --------------------------------------------------------
lab(
    "namespaces-dns",
    "🟡 Core 8 · Sail between harbors",
    "Switch the default namespace, find a Service's full DNS name and fix a cross-namespace client.",
    f"""
    # Sail between harbors

    Namespaces are separate harbors in one cluster. Inside a harbor you call a Service by its short name;
    **from another harbor you need the full address**.

    In namespace **`market`** there's a shop. In namespace **`docks`** a **`buyer`** keeps trying to reach it.

    Lesson: {L("1.18", "Namespaces")}
    """,
    [
        dict(
            title="Move into the market",
            text="""
            # Move into the market

            You'll work in `market` a lot. Make **`market`** the **default namespace** of your current context,
            so `kubectl get pods` shows the market without `-n`.
            """,
            hint="`kubectl config set-context --current --namespace=<ns>`",
            solution=cmd("kubectl config set-context --current --namespace=market\nkubectl get pods"),
            verify="""
            [ "$(kubectl config view --minify -o jsonpath='{..namespace}')" = "market" ] || exit 1
            """,
        ),
        dict(
            title="The full address",
            text="""
            # The full address

            Write the **fully qualified DNS name** of the Service `shop` in namespace `market`
            into **`/root/shop-fqdn.txt`**.
            """,
            hint="The pattern is `<service>.<namespace>.svc.<cluster-domain>`. The cluster domain is usually `cluster.local`.",
            solution=cmd("echo shop.market.svc.cluster.local > /root/shop-fqdn.txt"),
            verify="""
            got=$(tr -d '[:space:]' < /root/shop-fqdn.txt 2>/dev/null); got=${got%.}
            [ "$got" = "shop.market.svc.cluster.local" ] || exit 1
            """,
        ),
        dict(
            title="Help the buyer",
            text="""
            # Help the buyer 🔧

            The Deployment **`buyer`** in namespace **`docks`** can't reach the shop. Read its logs, find out why,
            and fix the **buyer** so its logs say `OK reached shop`.

            ⚠️ Don't move or copy the shop: fix the buyer.
            """,
            hint="`kubectl -n docks logs deploy/buyer` shows which URL it uses. The URL comes from an environment "
                 "variable: `kubectl -n docks set env deploy/buyer KEY=value` changes it.",
            solution=cmd("kubectl -n docks logs deploy/buyer --tail=3") + "\n\n" +
            cmd("kubectl -n docks set env deploy/buyer SHOP_URL=http://shop.market.svc.cluster.local\n"
                "kubectl -n docks rollout status deploy/buyer\nsleep 5; kubectl -n docks logs deploy/buyer --tail=3"),
            verify="""
            [ "$(kubectl get svc -A -l app=shop --no-headers | wc -l)" = "1" ] || exit 1
            kubectl -n market get svc shop >/dev/null 2>&1 || exit 1
            # a DNS name, not a hard-coded IP that breaks when the Service is recreated
            url=$(kubectl -n docks get deploy buyer -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="SHOP_URL")].value}')
            echo "$url" | grep -q 'shop\\.market' || exit 1
            kubectl -n docks rollout status deploy/buyer --timeout=5s >/dev/null 2>&1 || exit 1
            kubectl -n docks logs deploy/buyer --tail=2 2>/dev/null | grep -q 'OK reached shop' || exit 1
            """,
        ),
    ],
    done("""
    * Same namespace: `http://shop`. Another namespace: `http://shop.market` or the full
      `shop.market.svc.cluster.local`.
    * `kubectl config set-context --current --namespace=…` saves typing `-n` all day (very useful in the exam).
    * Namespaces separate names, not networks: any pod can reach any Service unless a NetworkPolicy says no.
    """, "Core 9 · Write YAML the fast way"),
    """
    kubectl create namespace market >/dev/null
    kubectl create namespace docks >/dev/null
    kubectl -n market create deployment shop --image=nginx:1.27 >/dev/null
    kubectl -n market expose deployment shop --port=80 >/dev/null
    kubectl -n market label svc shop app=shop --overwrite >/dev/null
    cat > /root/.buyer.yaml <<'EOF'
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: buyer
      namespace: docks
    spec:
      selector:
        matchLabels: {app: buyer}
      template:
        metadata:
          labels: {app: buyer}
        spec:
          containers:
          - name: buyer
            image: busybox:1.36
            env:
            - name: SHOP_URL
              value: http://shop
            command: ["sh", "-c", "while true; do if wget -qO- -T 2 $SHOP_URL >/dev/null 2>&1; then echo OK reached shop; else echo FAIL cannot reach $SHOP_URL; fi; sleep 3; done"]
    EOF
    kubectl apply -f /root/.buyer.yaml >/dev/null && rm /root/.buyer.yaml
    kubectl -n market wait --for=condition=Available deploy/shop --timeout=300s >/dev/null
    kubectl -n docks wait --for=condition=Available deploy/buyer --timeout=300s >/dev/null
    """,
)

# 9 · imperative vs declarative (1.19, 1.20) -----------------------------------
lab(
    "imperative-yaml",
    "🟡 Core 9 · Write YAML the fast way",
    "Generate YAML with --dry-run, find a field with kubectl explain and apply it declaratively.",
    f"""
    # Write YAML the fast way

    In the exam nobody types YAML from scratch. You **generate** it, **look up** the field you need,
    and **apply** it. That's what you'll practise here.

    Lessons: {L("1.19", "Imperative vs declarative")} · {L("1.20", "kubectl explain & apply")}
    """,
    [
        dict(
            title="Generate, don't type",
            text="""
            # Generate, don't type

            Write the YAML for a Deployment **`beacon`** (image **`nginx:1.27`**, **2 replicas**) into
            **`/root/beacon.yaml`**, using kubectl to generate it.

            ⚠️ Don't create the Deployment yet: only the file.
            """,
            hint="`kubectl create deployment … --dry-run=client -o yaml > file` prints the object instead of creating it.",
            solution=cmd("kubectl create deployment beacon --image=nginx:1.27 --replicas=2 --dry-run=client -o yaml > /root/beacon.yaml\ncat /root/beacon.yaml"),
            verify="""
            f=/root/beacon.yaml
            grep -q '^kind: Deployment' $f || exit 1
            grep -qE '^  name: beacon$' $f || exit 1
            grep -qE '^  replicas: 2$' $f || exit 1
            grep -q 'image: nginx:1.27' $f || exit 1
            kubectl get deploy beacon >/dev/null 2>&1 && exit 1
            exit 0
            """,
        ),
        dict(
            title="Look it up",
            text="""
            # Look it up

            The beacon must shut down quickly. Find the **pod-level field** that sets how many seconds a pod gets
            to stop gracefully, and set it to **15** in `/root/beacon.yaml`.

            Use `kubectl explain`, not Google. 😉
            """,
            hint="`kubectl explain pod.spec | grep -i grace`, then `kubectl explain deployment.spec.template.spec.<field>`. "
                 "It goes next to `containers:` in the pod template.",
            solution=cmd("kubectl explain pod.spec | grep -i -A2 grace") + "\n\n" +
            cmd("sed -i 's/^      containers:/      terminationGracePeriodSeconds: 15\\n      containers:/' /root/beacon.yaml\ngrep -B1 -A2 termination /root/beacon.yaml"),
            verify="""
            grep -qE '^      terminationGracePeriodSeconds: 15$' /root/beacon.yaml || exit 1
            kubectl apply -f /root/beacon.yaml --dry-run=server >/dev/null 2>&1 || exit 1
            """,
        ),
        dict(
            title="Apply it",
            text="""
            # Apply it

            Now create the beacon **declaratively** from your file, so later changes to the file can be applied again.
            """,
            hint="`kubectl apply -f` remembers what you applied (in an annotation); `kubectl create -f` doesn't.",
            solution=cmd("kubectl apply -f /root/beacon.yaml\nkubectl get deploy beacon -o yaml | grep -A1 last-applied | head -3"),
            verify="""
            [ "$(kubectl get deploy beacon -o jsonpath='{.status.readyReplicas}')" = "2" ] || exit 1
            [ "$(kubectl get deploy beacon -o jsonpath='{.spec.template.spec.terminationGracePeriodSeconds}')" = "15" ] || exit 1
            kubectl get deploy beacon -o jsonpath='{.metadata.annotations}' | grep -q 'last-applied-configuration' || exit 1
            """,
        ),
    ],
    done("""
    * `--dry-run=client -o yaml` turns any imperative command into a YAML starter file.
    * `kubectl explain <type>.<field>` documents every field, offline, in the exam.
    * `kubectl apply` stores the `last-applied-configuration` annotation, so it can compute changes next time.
    """, "Core 10 · The harbor is on fire (boss)"),
    "",
)

# 10 · boss (1.R) ---------------------------------------------------------------
lab(
    "harbor-on-fire",
    "🔴 Core 10 · The harbor is on fire",
    "Boss challenge: find and fix four hidden faults until visitors can reach the harbor page.",
    f"""
    # The harbor is on fire 🔥

    The harbor's web page is down and visitors are lining up. Several things are broken at once,
    and nobody tells you what. You have everything from Module 1: pods, ReplicaSets, Deployments, Services,
    namespaces, `describe`, `logs`.

    * The app lives in namespace **`harbor`** (Deployment and Service **`harbor-web`**).
    * The visitors are the Deployment **`visitor`** in namespace **`town`**.

    **Rules:** fix what's there. Don't create new Services or Deployments, and don't move anything to another namespace.

    Review: {L("1.R", "Module 1 review")}
    """,
    [
        dict(
            title="Bring the harbor back",
            text="""
            # Bring the harbor back 🔥

            Goal: from the node,
            `curl http://<harbor-web ClusterIP>` returns the nginx welcome page, served by **2 healthy pods**.

            Faults hidden here: **3**.
            """,
            hint="Work from the inside out: are the pods running (`kubectl -n harbor get pods`, `describe`)? "
                 "Does the Service find them (`kubectl -n harbor get endpointslices`)? "
                 "Does it send traffic to the right port (`kubectl -n harbor describe svc harbor-web`)?",
            solution=cmd("kubectl -n harbor get pods\nkubectl -n harbor describe pod -l app=harbor-web | grep -A2 -i failed") + "\n\n" +
            cmd("kubectl -n harbor set image deploy/harbor-web nginx=nginx:1.27-alpine\nkubectl -n harbor rollout status deploy/harbor-web") +
            "\n\n" + cmd("kubectl -n harbor patch svc harbor-web -p '{\"spec\":{\"selector\":{\"app\":\"harbor-web\"},\"ports\":[{\"port\":80,\"targetPort\":80}]}}'") +
            "\n\n" + cmd("curl -s http://$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.clusterIP}') | head -4"),
            verify="""
            [ "$(kubectl -n harbor get svc harbor-web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.harbor-svc-uid)" ] || exit 1
            [ "$(kubectl -n harbor get deploy harbor-web -o jsonpath='{.metadata.uid}')" = "$(cat /root/.harbor-deploy-uid)" ] || exit 1
            [ "$(kubectl -n harbor get deploy harbor-web -o jsonpath='{.status.readyReplicas}')" = "2" ] || exit 1
            ip=$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.clusterIP}')
            port=$(kubectl -n harbor get svc harbor-web -o jsonpath='{.spec.ports[0].port}')
            curl -s -m 3 "http://$ip:$port" | """ + NGINX_OK + """ || exit 1
            """,
        ),
        dict(
            title="Let the visitors in",
            text="""
            # Let the visitors in 🔥

            The harbor answers again, but the visitors still can't get in.
            Goal: `kubectl -n town logs deploy/visitor` says **`OK harbor reached`**.

            Faults hidden here: **1**.
            """,
            hint="Read the visitor's logs: which address does it use? Which namespace is it in, and which namespace is the harbor in?",
            solution=cmd("kubectl -n town logs deploy/visitor --tail=3") + "\n\n" +
            cmd("kubectl -n town set env deploy/visitor TARGET=http://harbor-web.harbor.svc.cluster.local\n"
                "kubectl -n town rollout status deploy/visitor\nsleep 5; kubectl -n town logs deploy/visitor --tail=3"),
            verify="""
            [ "$(kubectl get svc -A --no-headers | grep -c harbor-web)" = "1" ] || exit 1
            url=$(kubectl -n town get deploy visitor -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="TARGET")].value}')
            echo "$url" | grep -q 'harbor-web\\.harbor' || exit 1
            kubectl -n town rollout status deploy/visitor --timeout=5s >/dev/null 2>&1 || exit 1
            kubectl -n town logs deploy/visitor --tail=2 2>/dev/null | grep -q 'OK harbor reached' || exit 1
            """,
        ),
    ],
    done("""
    You fixed **four** faults like a real on-call engineer:

    1. a Deployment with an image tag that doesn't exist (`describe` → Events)
    2. a Service selector with a typo (no endpoints)
    3. a Service pointing at the wrong targetPort
    4. a client in another namespace using the short name

    That's Module 1 conquered. 🏆 Next on the course: [Module 2 · Scheduling](""" + SITE + """2.T)
    """),
    """
    kubectl create namespace harbor >/dev/null
    kubectl create namespace town >/dev/null
    kubectl -n harbor create deployment harbor-web --image=nginx:1.27-alpinee --replicas=2 >/dev/null
    kubectl -n harbor create service clusterip harbor-web --tcp=80:8080 >/dev/null
    kubectl -n harbor patch svc harbor-web -p '{"spec":{"selector":{"app":"harbor-wbe"}}}' >/dev/null
    kubectl -n harbor get svc harbor-web -o jsonpath='{.metadata.uid}' > /root/.harbor-svc-uid
    kubectl -n harbor get deploy harbor-web -o jsonpath='{.metadata.uid}' > /root/.harbor-deploy-uid
    cat > /root/.visitor.yaml <<'EOF'
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: visitor
      namespace: town
    spec:
      selector:
        matchLabels: {app: visitor}
      template:
        metadata:
          labels: {app: visitor}
        spec:
          containers:
          - name: visitor
            image: busybox:1.36
            env:
            - name: TARGET
              value: http://harbor-web
            command: ["sh", "-c", "while true; do if wget -qO- -T 2 $TARGET >/dev/null 2>&1; then echo OK harbor reached; else echo FAIL cannot reach $TARGET; fi; sleep 3; done"]
    EOF
    kubectl apply -f /root/.visitor.yaml >/dev/null && rm /root/.visitor.yaml
    kubectl -n town wait --for=condition=Available deploy/visitor --timeout=300s >/dev/null
    """,
)

labkit.structure(CORE, ["cluster-tour", "crictl-node", "etcd-peek", "pods-first", "replicasets", "deployments",
                        "services-fix", "namespaces-dns", "imperative-yaml", "harbor-on-fire"])
print("ok")
