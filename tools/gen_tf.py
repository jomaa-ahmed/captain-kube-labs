"""Generate the Shipwright Terraform lab pack (Modules 0-4) for Killercoda.

Every script uses $R (the lab root, /root on Killercoda) and $PY (python3), so the same labs run in
tools/test_tf.sh on a laptop with LABROOT/PY overridden. Each step carries:
  solve  - the commands of the right answer (also shown as the Solution, with $R -> /root)
  wrong  - a tempting wrong fix that verify.sh must reject (used only by the test harness)
Terraform 1.12.2 (the exam version) is installed in background.sh; only free local providers are used.
"""
import json, os, textwrap

import labkit
from labkit import ROOT, D

TF = os.path.join(ROOT, "terraform")
KC = "https://killercoda.com/captainkube/course/terraform/"
SITE_TF = "https://captains-academy.site/course/terraform/lesson/"
IMAGE = "ubuntu"
SPEC = []  # (folder, [steps with solve/wrong]) for the test harness

PRE = """\
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"
"""

INSTALL = """\
if ! command -v terraform >/dev/null 2>&1; then
  curl -fsSLo /tmp/tf.zip https://releases.hashicorp.com/terraform/1.12.2/terraform_1.12.2_linux_amd64.zip
  $PY -c "import zipfile; zipfile.ZipFile('/tmp/tf.zip').extractall('/usr/local/bin')"
  chmod +x /usr/local/bin/terraform
  grep -q TF_PLUGIN_CACHE_DIR /root/.bashrc 2>/dev/null || echo 'export TF_PLUGIN_CACHE_DIR=/root/.terraform.d/plugin-cache' >> /root/.bashrc
fi
"""

# helpers available to every verify.sh
VLIB = r"""
st() { terraform -chdir="$1" state list 2>/dev/null; }
noplan() { terraform -chdir="$1" plan -input=false -detailed-exitcode -lock=false >/dev/null 2>&1; }
attr() {  # attr DIR ADDRESS ATTRIBUTE -> value from the state
  terraform -chdir="$1" show -json 2>/dev/null | $PY -c "
import json,sys
d=json.load(sys.stdin); a,k=sys.argv[1],sys.argv[2]
for r in d.get('values',{}).get('root_module',{}).get('resources',[]):
    if r['address']==a: print(r['values'].get(k,'')); break" "$2" "$3"; }
serial() { $PY -c "import json,sys; print(json.load(open(sys.argv[1]))['serial'])" "$1/terraform.tfstate" 2>/dev/null || echo 0; }
"""


def tf_lab(folder, title, description, intro, steps, finish, setup):
    bg = PRE + INSTALL + textwrap.dedent(setup).lstrip("\n")
    st = []
    for s in steps:
        s2 = dict(s)
        s2["solution"] = labkit.cmd(textwrap.dedent(s["solve"]).strip().replace("$R", "/root"))
        s2["verify"] = PRE + VLIB + textwrap.dedent(s["verify"]).lstrip("\n")
        if s.get("background"):
            s2["background"] = PRE + textwrap.dedent(s["background"]).lstrip("\n")
        st.append(s2)
    labkit.lab(TF, folder, title, description, intro, st, finish, bg, image=IMAGE)
    SPEC.append({"folder": folder, "steps": [{"solve": textwrap.dedent(s["solve"]).strip(),
                                              "wrong": textwrap.dedent(s.get("wrong", "")).strip()} for s in steps]})


def L(code, name):
    return f"[{code} {name}]({SITE_TF}{code})"


def done(text, next_lab=None):
    tail = f"\n\nNext lab: **{next_lab}** ⚒" if next_lab else ""
    return f"# ⚒ Well built, Shipwright!\n\n{D(text)}{tail}\n"


def hcl(path_var, text):
    """Shell that writes an HCL file (quoted heredoc: nothing expands)."""
    return f"cat > {path_var} <<'HCL'\n{textwrap.dedent(text).strip()}\nHCL\n"


# 1 · first apply -------------------------------------------------------------------------------
tf_lab(
    "first-apply",
    "🟢 Terraform 1 · Your first build",
    "init, apply, and watch Terraform rebuild what was deleted by hand.",
    f"""
    # Your first build

    The shipyard is open. In `/root/shipyard` there's a blueprint, `main.tf`, with one resource:
    a local file called `hello.txt`.

    In this lab you will:
    1. Build it with **init** and **apply**
    2. See the three truths in action when someone deletes the file by hand

    Lessons: {L("0.2", "The three truths")} · {L("0.3", "Install Terraform")} · {L("3.1", "Write, plan, apply")}
    """,
    [
        {"title": "Build it",
         "text": """
         Go to `/root/shipyard`, prepare the folder and build the blueprint.

         When you're done, `hello.txt` must exist and the state must list `local_file.hello`.
         """,
         "hint": "Two commands: one prepares the folder (downloads the provider), one builds. Add `-auto-approve` or type `yes`.",
         "solve": "cd $R/shipyard\nterraform init\nterraform apply -auto-approve",
         "wrong": "cd $R/shipyard\necho 'Hello, shipyard!' > hello.txt",
         "verify": """
         st $R/shipyard | grep -qx local_file.hello || exit 1
         [ "$(cat $R/shipyard/hello.txt)" = "Hello, shipyard!" ] || exit 1
         """},
        {"title": "The ship sinks",
         "background": """
         rm -f $R/shipyard/hello.txt
         """,
         "text": """
         Someone deleted `hello.txt` by hand. 🌊

         Run a **plan** first and read it: what does Terraform want to do, and why?
         Then bring the file back **the Terraform way**, so the plan ends with *No changes*.

         ⛔ Writing the file by hand doesn't count: the ledger (state) must record the rebuild.
         """,
         "hint": "`terraform plan` shows `+ create`: the blueprint and the ledger say *a file*, the real world says *nothing*. Apply it.",
         "solve": "cd $R/shipyard\nterraform plan\nterraform apply -auto-approve",
         "wrong": "cd $R/shipyard\necho 'Hello, shipyard!' > hello.txt",
         "verify": """
         # exact bytes: Terraform writes no trailing newline, echo by hand does
         $PY -c "import sys; sys.exit(open(sys.argv[1],'rb').read()!=b'Hello, shipyard!')" "$R/shipyard/hello.txt" 2>/dev/null || exit 1
         noplan $R/shipyard || exit 1
         """},
    ],
    done("""
    You used the whole loop: **init → plan → apply**. And you saw the three truths: the blueprint (main.tf),
    the ledger (terraform.tfstate) and the real world (hello.txt). Plan compared them, apply closed the gap.
    """, "Fix the blueprint"),
    setup=f"""
    mkdir -p $R/shipyard && cd $R/shipyard
    {hcl("main.tf", '''
    resource "local_file" "hello" {
      filename = "${path.module}/hello.txt"
      content  = "Hello, shipyard!"
    }
    ''')}
    """,
)

# 2 · fix the blueprint ---------------------------------------------------------------------------
tf_lab(
    "fix-the-blueprint",
    "🔧 Terraform 2 · Fix the blueprint",
    "A broken config: make terraform validate pass, then build it.",
    f"""
    # Fix the blueprint

    A new apprentice wrote `/root/blueprint/main.tf`. It doesn't even validate.
    There are **two** mistakes in it, both classic.

    Lessons: {L("2.1", "Anatomy of a block")} · {L("2.2", "Your first resource")} · {L("3.3", "terraform validate")}
    """,
    [
        {"title": "Make it valid",
         "text": """
         In `/root/blueprint`, run `terraform validate` and read every error.
         Fix the file until validate says **Success**.

         ⛔ Keep the `local_file` resource called `note` and keep its `lifecycle` settings: fix them, don't delete them.
         """,
         "hint": "validate needs the provider schema first. Then: a nested block has **no equals sign**. And check the spelling of every argument name.",
         "solve": "cd $R/blueprint\nterraform init\nsed -i 's/lifecycle = {/lifecycle {/; s/filname /filename/' main.tf\nterraform fmt\nterraform validate",
         "wrong": "cd $R/blueprint\nterraform init\nprintf 'resource \"local_file\" \"note\" {\\n  filename = \"note.txt\"\\n  content  = \"x\"\\n}\\n' > main.tf",
         "verify": """
         cd $R/blueprint
         terraform validate >/dev/null 2>&1 || exit 1
         grep -Eq '^resource "local_file" "note"' main.tf || exit 1
         grep -Eq '^\\s*lifecycle\\s*\\{' main.tf || exit 1
         grep -Eq 'create_before_destroy\\s*=\\s*true' main.tf || exit 1
         """},
        {"title": "Build it",
         "text": "Now build it, so `note.txt` exists and the plan says *No changes*.",
         "hint": "One command builds what's planned.",
         "solve": "cd $R/blueprint\nterraform apply -auto-approve",
         "wrong": "cd $R/blueprint\necho 'A valid blueprint' > note.txt",
         "verify": """
         st $R/blueprint | grep -qx local_file.note || exit 1
         [ -f $R/blueprint/note.txt ] || exit 1
         noplan $R/blueprint || exit 1
         """},
    ],
    done("""
    `validate` caught both mistakes locally, without touching anything real.
    Remember: `lifecycle { }` is a **block** (no `=`), `tags = { }` would be an argument holding a map.
    """, "References build the order"),
    setup=f"""
    mkdir -p $R/blueprint && cd $R/blueprint
    {hcl("main.tf", '''
    resource "local_file" "note" {
      filname = "${path.module}/note.txt"
      content = "A valid blueprint"

      lifecycle = {
        create_before_destroy = true
      }
    }
    ''')}
    """,
)

# 3 · references -----------------------------------------------------------------------------------
tf_lab(
    "references",
    "🟡 Terraform 3 · References build the order",
    "Link two resources with a reference and let Terraform order them.",
    f"""
    # References build the order

    In `/root/references` there are two resources: a random pet name `ship`, and a file `manifest`
    that should say which ship it belongs to. Right now it says `Ship: CHANGE-ME`.

    Lessons: {L("2.3", "References build the order")} · {L("3.5", "The resource graph")}
    """,
    [
        {"title": "Link them",
         "text": """
         Make the manifest's content **`Ship: <the pet's id>`**, using a **reference** to the random pet,
         then apply. Watch the order of the *Creating...* lines.

         ⛔ Don't type the pet name into the file: the blueprint must reference it.
         """,
         "hint": "A reference is `type.name.attribute`. Inside a string: `\"Ship: ${random_pet.ship.id}\"`.",
         "solve": "cd $R/references\nsed -i 's/CHANGE-ME/${random_pet.ship.id}/' main.tf\nterraform init\nterraform apply -auto-approve",
         "wrong": "cd $R/references\nsed -i 's/CHANGE-ME/brave-ship/' main.tf\nterraform init\nterraform apply -auto-approve",
         "verify": """
         cd $R/references
         grep -q 'random_pet.ship.id' main.tf || exit 1
         pet=$(attr . random_pet.ship id); [ -n "$pet" ] || exit 1
         [ "$(cat manifest.txt 2>/dev/null)" = "Ship: $pet" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    The reference made an **implicit dependency**: Terraform created the pet first, then the manifest,
    without you writing any order. Try `terraform graph` to see the arrow.
    """, "Layout and fmt"),
    setup=f"""
    mkdir -p $R/references && cd $R/references
    {hcl("main.tf", '''
    resource "random_pet" "ship" {}

    resource "local_file" "manifest" {
      filename = "${path.module}/manifest.txt"
      content  = "Ship: CHANGE-ME"
    }
    ''')}
    """,
)

# 4 · layout and fmt ---------------------------------------------------------------------------------
tf_lab(
    "layout-and-fmt",
    "🟢 Terraform 4 · File layout and fmt",
    "Split one messy file into the standard files and make fmt happy.",
    f"""
    # File layout and fmt

    `/root/layout/all.tf` holds everything in one messy file. Your crew wants the standard layout.

    Lessons: {L("2.4", "File layout")} · {L("2.5", "terraform fmt and style")}
    """,
    [
        {"title": "Split and format",
         "text": """
         In `/root/layout`:
         - the `terraform` block goes into **terraform.tf**
         - the resource goes into **main.tf**
         - the output goes into **outputs.tf**
         - `all.tf` is gone

         Then `terraform fmt -check` must pass and `terraform validate` must say Success.
         """,
         "hint": "File names don't matter to Terraform, only to people. `terraform fmt` fixes the spacing for you.",
         "solve": """cd $R/layout
cat > terraform.tf <<'HCL'
terraform {
  required_providers {
    local = { source = "hashicorp/local" }
  }
}
HCL
cat > main.tf <<'HCL'
resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = "Crew of the shipyard"
}
HCL
cat > outputs.tf <<'HCL'
output "crew_file" {
  value = local_file.crew.filename
}
HCL
rm all.tf
terraform fmt
terraform init
terraform validate""",
         "wrong": "cd $R/layout\nterraform fmt\nterraform init\nterraform validate",
         "verify": """
         cd $R/layout
         [ ! -f all.tf ] || exit 1
         grep -q '^terraform {' terraform.tf 2>/dev/null || exit 1
         grep -q '^resource "local_file" "crew"' main.tf 2>/dev/null || exit 1
         grep -q '^output "crew_file"' outputs.tf 2>/dev/null || exit 1
         terraform fmt -check -recursive >/dev/null 2>&1 || exit 1
         terraform validate >/dev/null 2>&1 || exit 1
         """},
    ],
    done("""
    Same configuration, now in the files every Terraform engineer expects. `fmt -check` is what a pipeline runs:
    it fails the build when the layout is off, without changing anything.
    """, "Read the plan"),
    setup=f"""
    mkdir -p $R/layout && cd $R/layout
    {hcl("all.tf", '''
    terraform {
    required_providers {
        local = { source = "hashicorp/local" }
      }
    }
    resource "local_file" "crew" {
        filename = "${path.module}/crew.txt"
     content = "Crew of the shipyard"
    }
    output "crew_file" {
    value = local_file.crew.filename
    }
    ''')}
    """,
)

# 5 · read the plan ------------------------------------------------------------------------------------
PLAN_V1 = '''
resource "terraform_data" "update_me" {
  input = "v1"
}

resource "local_file" "replace_me" {
  filename = "${path.module}/a.txt"
  content  = "v1"
}

resource "local_file" "delete_me" {
  filename = "${path.module}/b.txt"
  content  = "bye"
}
'''
PLAN_V2 = '''
resource "terraform_data" "update_me" {
  input = "v2"
}

resource "local_file" "replace_me" {
  filename = "${path.module}/a.txt"
  content  = "v2"
}

resource "local_file" "create_me" {
  filename = "${path.module}/c.txt"
  content  = "new"
}
'''
tf_lab(
    "read-the-plan",
    "🟡 Terraform 5 · Read the plan",
    "Read every plan symbol, answer, then apply exactly the plan you saved.",
    f"""
    # Read the plan

    In `/root/plan` the blueprint was changed since the last build. Before anything is applied,
    the crew wants the work order read out loud.

    Lesson: {L("3.4", "Reading a plan")}
    """,
    [
        {"title": "Read it",
         "text": """
         Run `terraform plan` in `/root/plan` and write your answers in `/root/answers/`:
         - `replaced.txt`: the address of the resource that will be **replaced** (-/+)
         - `destroyed.txt`: the address of the resource that will be **destroyed** only (-)
         - `add.txt`: the number in the summary line after **to add**
         """,
         "hint": "Look for `must be replaced` and `will be destroyed`. A replacement also counts in *to add*.",
         "solve": "cd $R/plan\nterraform plan\nmkdir -p $R/answers\necho local_file.replace_me > $R/answers/replaced.txt\necho local_file.delete_me > $R/answers/destroyed.txt\necho 2 > $R/answers/add.txt",
         "wrong": "mkdir -p $R/answers\necho local_file.replace_me > $R/answers/replaced.txt\necho local_file.delete_me > $R/answers/destroyed.txt\necho 1 > $R/answers/add.txt",
         "verify": """
         a=$R/answers
         [ "$(tr -d ' \\r\\n' < $a/replaced.txt 2>/dev/null)" = "local_file.replace_me" ] || exit 1
         [ "$(tr -d ' \\r\\n' < $a/destroyed.txt 2>/dev/null)" = "local_file.delete_me" ] || exit 1
         [ "$(tr -d ' \\r\\n' < $a/add.txt 2>/dev/null)" = "2" ] || exit 1
         """},
        {"title": "Apply the saved plan",
         "text": """
         Save the plan to a file called `tfplan` in `/root/plan`, then apply **that file**.
         Afterwards the plan must say *No changes*.
         """,
         "hint": "`terraform plan -out=tfplan`, then `terraform apply tfplan` (no question asked).",
         "solve": "cd $R/plan\nterraform plan -out=tfplan\nterraform apply tfplan",
         "wrong": "cd $R/plan\nterraform apply -auto-approve",
         "verify": """
         cd $R/plan
         [ -f tfplan ] || exit 1
         noplan . || exit 1
         [ "$(cat c.txt 2>/dev/null)" = "new" ] && [ ! -f b.txt ] || exit 1
         """},
    ],
    done("""
    `+` create · `~` update in place · `-/+` replace · `-` destroy. And a replacement counts twice in the summary.
    A saved plan applies exactly what you reviewed.
    """, "Half built"),
    setup=f"""
    mkdir -p $R/plan && cd $R/plan
    {hcl("main.tf", PLAN_V1)}
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    {hcl("main.tf", PLAN_V2)}
    """,
)

# 6 · half built (partial apply) ----------------------------------------------------------------------
tf_lab(
    "half-built",
    "🔧 Terraform 6 · Half built",
    "An apply failed halfway. Finish the job without rebuilding what already stands.",
    f"""
    # Half built

    A storm hit the shipyard: the last `apply` in `/root/halfbuilt` **failed halfway**.
    The ship (`random_pet.ship`) was built. The logbook file was not.

    Lesson: {L("3.6", "terraform apply")}
    """,
    [
        {"title": "Finish the job",
         "text": """
         Read the error (`terraform apply` again shows it), fix the cause **in the blueprint**, and finish the apply.

         ⛔ The ship that's already built must **stay**: same pet name as before, no destroy, no `-replace`.
         ⛔ Don't delete the file called `logs`: it belongs to another crew.
         """,
         "hint": "The logbook's path goes through `logs`, which is a **file**, not a folder. Put the logbook in another folder, for example `logbook/today.txt`.",
         "solve": "cd $R/halfbuilt\nterraform apply -auto-approve || true\nsed -i 's#logs/today.txt#logbook/today.txt#' main.tf\nterraform apply -auto-approve",
         "wrong": "cd $R/halfbuilt\nsed -i 's#logs/today.txt#logbook/today.txt#' main.tf\nterraform destroy -auto-approve\nterraform apply -auto-approve",
         "verify": """
         cd $R/halfbuilt
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/pet_id)" ] || exit 1
         st . | grep -qx local_file.logbook || exit 1
         [ -f logs ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Terraform has **no rollback**: what succeeded stayed in the state. You fixed the cause and applied again,
    and Terraform only built what was missing.
    """, "Remove one thing"),
    setup=f"""
    mkdir -p $R/halfbuilt && cd $R/halfbuilt
    echo "another crew's notes" > logs
    {hcl("main.tf", '''
    resource "random_pet" "ship" {}

    resource "local_file" "logbook" {
      filename = "${path.module}/logs/today.txt"
      content  = "Ship ${random_pet.ship.id} launched"
    }
    ''')}
    terraform init -input=false >/dev/null
    terraform apply -auto-approve -input=false >/dev/null 2>&1 || true
    terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['id'] for r in d['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/pet_id
    """,
)

# 7 · remove one -----------------------------------------------------------------------------------------
tf_lab(
    "remove-one",
    "🟢 Terraform 7 · Remove one thing",
    "Retire one resource the everyday way, without destroying the rest.",
    f"""
    # Remove one thing

    In `/root/dismantle` the shipyard manages three parts: `hull`, `mast` and an `old_boat`.
    Next to them lies `neighbor.txt`, made by hand by another shipyard.

    Lesson: {L("3.7", "terraform destroy")}
    """,
    [
        {"title": "Retire the old boat",
         "text": """
         Remove **only** the old boat: `old_boat.txt` must disappear and leave the state.

         ⛔ `hull`, `mast` and `neighbor.txt` must stay.
         """,
         "hint": "Delete the old boat's block from `main.tf`, then apply: the plan says *will be destroyed, because it's not in configuration*.",
         "solve": """cd $R/dismantle
$PY - <<'PY'
import re
p='main.tf'; t=open(p).read()
t=re.sub(r'resource "local_file" "old_boat" \\{.*?\\n\\}\\n?', '', t, flags=re.S)
open(p,'w').write(t)
PY
terraform apply -auto-approve""",
         "wrong": "cd $R/dismantle\nterraform destroy -auto-approve",
         "verify": """
         cd $R/dismantle
         s=$(st .)
         echo "$s" | grep -qx local_file.hull && echo "$s" | grep -qx local_file.mast || exit 1
         ! echo "$s" | grep -qx local_file.old_boat || exit 1
         [ ! -f old_boat.txt ] && [ -f hull.txt ] && [ -f mast.txt ] && [ -f neighbor.txt ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Deleting a block and applying is how you retire one resource every day.
    `terraform destroy` removes **everything** in the state, and nothing that isn't in it (like neighbor.txt).
    """, "Versions and the lock file"),
    setup=f"""
    mkdir -p $R/dismantle && cd $R/dismantle
    echo "built by hand next door" > neighbor.txt
    {hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "hull"
    }

    resource "local_file" "mast" {
      filename = "${path.module}/mast.txt"
      content  = "mast"
    }

    resource "local_file" "old_boat" {
      filename = "${path.module}/old_boat.txt"
      content  = "old boat"
    }
    ''')}
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 8 · versions and the lock file -----------------------------------------------------------------------------
tf_lab(
    "versions-lock",
    "🔧 Terraform 8 · Versions and the lock file",
    "The constraint changed and init refuses. Move to the new version the right way.",
    f"""
    # Versions and the lock file

    The crew in `/root/versions` decided to stay on the **2.4** line of the `hashicorp/local` provider
    and changed the constraint to `~> 2.4.0`. Now `terraform init` fails.

    Lessons: {L("4.2", "Pinning versions")} · {L("4.3", "The lock file")}
    """,
    [
        {"title": "Unlock the upgrade",
         "text": """
         Make `terraform init` succeed with a **2.4.x** version of the local provider.

         ⛔ Keep the constraint `~> 2.4.0`. ⛔ Don't edit or delete `.terraform.lock.hcl` by hand.
         """,
         "hint": "Read init's error: the lock file still says 2.9.x. `init -upgrade` picks the newest version the constraint allows and rewrites the lock.",
         "solve": "cd $R/versions\nterraform init || true\nterraform init -upgrade",
         "wrong": "cd $R/versions\nsed -i 's/version     = \"2\\.[0-9]*\\.[0-9]*\"/version     = \"2.4.1\"/' .terraform.lock.hcl\nterraform init",
         "verify": """
         cd $R/versions
         grep -q 'version = "~> 2.4.0"' main.tf || exit 1
         grep -Eq 'version\\s+= "2\\.4\\.[0-9]+"' .terraform.lock.hcl || exit 1
         grep -q 'constraints = "~> 2.4.0"' .terraform.lock.hcl || exit 1
         terraform init -input=false >/dev/null 2>&1 || exit 1
         """},
    ],
    done("""
    The lock file pins the exact version for the whole team. You moved on purpose with `init -upgrade`,
    which rewrote it with the new version **and** its checksums.
    """, "Two harbors"),
    setup=f"""
    mkdir -p $R/versions && cd $R/versions
    {hcl("main.tf", '''
    terraform {
      required_providers {
        local = {
          source  = "hashicorp/local"
          version = "~> 2.4"
        }
      }
    }
    ''')}
    terraform init -input=false >/dev/null
    sed -i 's/version = "~> 2.4"/version = "~> 2.4.0"/' main.tf
    """,
)

# 9 · two harbors (alias) -----------------------------------------------------------------------------------------
tf_lab(
    "two-harbors",
    "🟡 Terraform 9 · Two harbors",
    "Use a second configuration of the same provider with alias.",
    f"""
    # Two harbors

    The shipyard writes its records with the `hashicorp/local` provider. Now there's a second harbor:
    the **backup** harbor. In `/root/harbors` one file is already managed.

    Lesson: {L("4.5", "Multiple providers and alias")}
    """,
    [
        {"title": "Add the backup harbor",
         "text": """
         Add a second `local` provider configuration with **alias `backup`**, and a new resource
         `local_file` called `backup` that writes `backup.txt` (any content) **through that alias**. Apply.
         """,
         "hint": "`provider \"local\" { alias = \"backup\" }`, then in the resource: `provider = local.backup` (no quotes).",
         "solve": """cd $R/harbors
cat >> main.tf <<'HCL'

provider "local" {
  alias = "backup"
}

resource "local_file" "backup" {
  provider = local.backup
  filename = "${path.module}/backup.txt"
  content  = "backup records"
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/harbors
cat >> main.tf <<'HCL'

resource "local_file" "backup" {
  filename = "${path.module}/backup.txt"
  content  = "backup records"
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/harbors
         [ -f backup.txt ] || exit 1
         $PY - "$R/harbors/terraform.tfstate" <<'PY' || exit 1
import json,sys
s=json.load(open(sys.argv[1]))
ok=[r for r in s["resources"] if r["type"]=="local_file" and r["name"]=="backup" and r["provider"].endswith('.backup')]
sys.exit(0 if ok else 1)
PY
         noplan . || exit 1
         """},
    ],
    done("""
    The default configuration has no alias. Every extra one needs `alias`, and resources choose it with
    `provider = <name>.<alias>`. With AWS, that's how you reach a second region or account.
    """, "BOSS · Shipyard in trouble"),
    setup=f"""
    mkdir -p $R/harbors && cd $R/harbors
    {hcl("main.tf", '''
    resource "local_file" "main_records" {
      filename = "${path.module}/main.txt"
      content  = "main harbor records"
    }
    ''')}
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 10 · boss -------------------------------------------------------------------------------------------------------------
tf_lab(
    "shipyard-in-trouble",
    "🔴 Terraform BOSS · Shipyard in trouble",
    "Several hidden faults, one goal: a clean, valid, fully built shipyard.",
    f"""
    # 🔴 BOSS · Shipyard in trouble

    The shipyard in `/root/boss` is a mess, and nobody remembers why. You only get the **goal**.

    Covers Modules 2-4: {L("2.1", "Blocks")} · {L("2.5", "fmt")} · {L("3.4", "Plans")} · {L("4.3", "Lock file")}
    """,
    [
        {"title": "Get it shipshape",
         "text": """
         In `/root/boss`, reach this state:
         - `terraform fmt -check` passes and `terraform validate` says Success
         - the local provider is on the **2.4.x** line that `main.tf` asks for
         - `cargo.txt` says exactly **`Ship: <the pet's id>`**
         - `terraform plan` says **No changes**

         ⛔ The ship (`random_pet.ship`) is already built: keep the same pet. ⛔ No hand edits of the lock file.
         """,
         "hint": "Go fault by fault: init (read the error), validate (read the errors), plan (read every symbol). One file went missing by hand...",
         "solve": "cd $R/boss\nterraform init -upgrade\nsed -i 's/lifecycle = {/lifecycle {/' main.tf\nterraform fmt\nterraform validate\nterraform apply -auto-approve",
         "wrong": "cd $R/boss\nrm -f .terraform.lock.hcl\nsed -i 's/lifecycle = {/lifecycle {/' main.tf\nterraform fmt\nterraform init\nterraform destroy -auto-approve\nterraform apply -auto-approve",
         "verify": """
         cd $R/boss
         terraform fmt -check >/dev/null 2>&1 || exit 1
         terraform validate >/dev/null 2>&1 || exit 1
         grep -Eq 'version\\s+= "2\\.4\\.[0-9]+"' .terraform.lock.hcl || exit 1
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/boss_pet)" ] || exit 1
         [ "$(cat cargo.txt 2>/dev/null)" = "Ship: $(cat /tmp/boss_pet)" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    You read init's error, validate's errors and the plan, and fixed each truth: the blueprint, the ledger and the
    real world. That's the whole job of a Terraform engineer. Modules 0-4: done. ⚒
    """),
    setup=f"""
    mkdir -p $R/boss && cd $R/boss
    {hcl("main.tf", '''
    terraform {
      required_providers {
        local = {
          source  = "hashicorp/local"
          version = "~> 2.4"
        }
        random = { source = "hashicorp/random" }
      }
    }

    resource "random_pet" "ship" {}

    resource "local_file" "cargo" {
      filename = "${path.module}/cargo.txt"
      content  = "Ship: ${random_pet.ship.id}"
    }
    ''')}
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['id'] for r in d['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/boss_pet
    # the faults: a stricter constraint than the lock, a nested block written with =, messy spacing, drift
    {hcl("main.tf", '''
    terraform {
      required_providers {
        local = {
          source  = "hashicorp/local"
          version = "~> 2.4.0"
        }
        random = { source = "hashicorp/random" }
      }
    }

    resource "random_pet" "ship" {}

    resource "local_file" "cargo" {
        filename = "${path.module}/cargo.txt"
      content = "Ship: ${random_pet.ship.id}"

      lifecycle = {
        create_before_destroy = true
      }
    }
    ''')}
    rm -f cargo.txt
    """,
)

ORDER = ["first-apply", "fix-the-blueprint", "references", "layout-and-fmt", "read-the-plan", "half-built",
         "remove-one", "versions-lock", "two-harbors", "shipyard-in-trouble"]
labkit.structure(TF, ORDER)
with open(os.path.join(ROOT, "tools", "tf_spec.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(SPEC, f, indent=1)

LINKS = {"0.2": "first-apply", "0.3": "first-apply", "3.1": "first-apply", "2.1": "fix-the-blueprint",
         "2.2": "fix-the-blueprint", "3.3": "fix-the-blueprint", "2.3": "references", "3.5": "references",
         "2.4": "layout-and-fmt", "2.5": "layout-and-fmt", "3.4": "read-the-plan", "3.6": "half-built",
         "3.7": "remove-one", "4.2": "versions-lock", "4.3": "versions-lock", "4.5": "two-harbors",
         "3.R": "shipyard-in-trouble", "4.R": "shipyard-in-trouble"}
with open(os.path.join(ROOT, "labs-terraform.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"_comment": "Terraform lesson code -> Killercoda lab URL (lab_links.py --course terraform)",
               **{k: KC + v for k, v in LINKS.items()}}, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"wrote {len(ORDER)} Terraform labs in {TF}")
