"""Shared helpers for the Captain Kube lab generators (one Killercoda scenario per lab)."""
import json, os, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://captains-academy.site/course/kubernetes/lesson/"

# Killercoda courses in the order they appear on killercoda.com/captainkube
COURSES = [
    ("core", "Captain Kube · Module 1 · Core Concepts"),
    ("scheduling", "Captain Kube · Module 2 · Scheduling"),
    ("helm", "Captain Kube · Module 10 · Helm"),
    ("terraform", "The Shipwright · Terraform · Modules 0-8"),
]

FOREGROUND = """\
echo "⚓ Captain Kube is preparing your harbor..."
while [ ! -f /tmp/finished ]; do sleep 1; done
clear
echo "⚓ Ready. Read the task on the left and get to work, Captain!"
"""


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(textwrap.dedent(text).lstrip("\n"))


def D(x):
    return textwrap.dedent(x).strip()


def details(text, body):
    return f"<details><summary>{text}</summary>\n\n{body.strip()}\n\n</details>\n"


def cmd(c):
    return f"```plain\n{c.strip()}\n```{{{{exec}}}}"


def lab(course_dir, folder, title, description, intro, steps, finish, background,
        image="kubernetes-kubeadm-1node"):
    """Write one scenario. background prepares the cluster (touch /tmp/finished is added).
    A step may carry its own "background" script, run when the learner reaches that step."""
    d = os.path.join(course_dir, folder)
    step_idx = []
    for i, s in enumerate(steps, 1):
        e = {"title": s["title"], "text": f"step{i}/text.md", "verify": f"step{i}/verify.sh"}
        if s.get("background"):
            e["background"] = f"step{i}/background.sh"
        step_idx.append(e)
    idx = {
        "title": title,
        "description": description,
        "details": {
            "intro": {"text": "intro.md", "background": "background.sh", "foreground": "foreground.sh"},
            "steps": step_idx,
            "finish": {"text": "finish.md"},
        },
        "backend": {"imageid": image},
    }
    w(os.path.join(d, "index.json"), json.dumps(idx, indent=2, ensure_ascii=False) + "\n")
    w(os.path.join(d, "intro.md"), intro)
    w(os.path.join(d, "finish.md"), finish)
    w(os.path.join(d, "foreground.sh"), FOREGROUND)
    w(os.path.join(d, "background.sh"), "#!/bin/bash\n" + background + "touch /tmp/finished\n")
    for i, s in enumerate(steps, 1):
        text = D(s["text"]) + "\n\n<br>\n\n" + details("💡 Hint", D(s["hint"])) + "\n" + details("Solution", s["solution"])
        w(os.path.join(d, f"step{i}", "text.md"), text)
        w(os.path.join(d, f"step{i}", "verify.sh"), "#!/bin/bash\n" + textwrap.dedent(s["verify"]).lstrip("\n"))
        if s.get("background"):
            w(os.path.join(d, f"step{i}", "background.sh"), "#!/bin/bash\n" + textwrap.dedent(s["background"]).lstrip("\n"))


def structure(course_dir, labs):
    """Lab order inside one course, plus the repo-level course list."""
    w(os.path.join(course_dir, "structure.json"), json.dumps({"items": [{"path": p} for p in labs]}, indent=2) + "\n")
    w(os.path.join(ROOT, "structure.json"),
      json.dumps({"items": [{"path": p, "title": t} for p, t in COURSES]}, indent=2, ensure_ascii=False) + "\n")
