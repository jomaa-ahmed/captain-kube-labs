"""Test the Terraform labs end to end on a laptop (no Killercoda needed).

usage: python tools/test_tf.py [lab ...] [--root DIR]
Needs bash and terraform on PATH (Terraform 1.12.x). For every lab and every step it checks that
  1. the solution passes verify.sh, after the earlier steps were solved, and
  2. the tempting wrong fix fails verify.sh (on a fresh setup).
Scripts run with LABROOT=<root>/<lab> instead of /root, PY=<this python>.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TF = os.path.join(ROOT, "terraform")


BASH = os.environ.get("BASH_EXE") or (os.path.join(os.environ.get("ProgramFiles", "C:/Program Files"), "Git", "bin", "bash.exe") if os.name == "nt" else "bash")  # not WSL's bash.exe


PRE = 'R="$LABROOT"; PY="${PY:-python3}"\n'  # the solutions use $R and $PY like the lab scripts


def bash(script, env, cwd):
    return subprocess.run([BASH, "-c", script], env=env, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def unix(p):  # C:\x\y -> /c/x/y for Git Bash
    p = p.replace("\\", "/")
    return "/" + p[0].lower() + p[2:] if len(p) > 1 and p[1] == ":" else p


def run_file(path, env, cwd):
    return bash(open(path, encoding="utf-8").read(), env, cwd)


def fresh(lab, base, env):
    root = os.path.join(base, lab)
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    e = dict(env, LABROOT=unix(root))
    r = run_file(os.path.join(TF, lab, "background.sh"), e, root)
    if r.returncode:
        raise SystemExit(f"{lab}: background.sh failed\n{r.stdout[-800:]}\n{r.stderr[-800:]}")
    return root, e


def step_bg(lab, i, e, root):
    p = os.path.join(TF, lab, f"step{i}", "background.sh")
    if os.path.exists(p):
        run_file(p, e, root)


def verify(lab, i, e, root):
    return run_file(os.path.join(TF, lab, f"step{i}", "verify.sh"), e, root).returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("labs", nargs="*")
    ap.add_argument("--root", default=os.path.join(tempfile.gettempdir(), "tf-labs-test"))
    a = ap.parse_args()
    spec = json.load(open(os.path.join(ROOT, "tools", "tf_spec.json"), encoding="utf-8"))
    env = dict(os.environ, PY=unix(sys.executable), TF_IN_AUTOMATION="1",
               TF_PLUGIN_CACHE_DIR=unix(os.path.join(a.root, "_plugin-cache")))
    os.makedirs(os.path.join(a.root, "_plugin-cache"), exist_ok=True)
    bad = 0
    for lab in spec:
        name, steps = lab["folder"], lab["steps"]
        if a.labs and name not in a.labs:
            continue
        # right path: solve every step in order
        root, e = fresh(name, a.root, env)
        for i, s in enumerate(steps, 1):
            step_bg(name, i, e, root)
            bash(PRE + s["solve"], e, root)
            ok = verify(name, i, e, root)
            print(f"{'PASS' if ok else 'FAIL'}  {name} step {i}: solution passes")
            bad += not ok
        # wrong fixes: fresh setup, earlier steps solved, then the wrong fix
        for i, s in enumerate(steps, 1):
            if not s["wrong"]:
                continue
            root, e = fresh(name, a.root, env)
            for j, prev in enumerate(steps[: i - 1], 1):
                step_bg(name, j, e, root)
                bash(PRE + prev["solve"], e, root)
            step_bg(name, i, e, root)
            bash(PRE + s["wrong"], e, root)
            ok = not verify(name, i, e, root)
            print(f"{'PASS' if ok else 'FAIL'}  {name} step {i}: wrong fix is rejected")
            bad += not ok
    print(f"\n{'all good' if not bad else str(bad) + ' problem(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
