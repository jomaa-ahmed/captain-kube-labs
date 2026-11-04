"""Generate the Shipwright Terraform lab pack (Modules 0-5) for Killercoda.

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

# course order (Killercoda shows labs in this order); titles "Terraform # · ..." are numbered from it, bosses aren't
ORDER = ["first-apply", "fix-the-blueprint", "references", "layout-and-fmt", "read-the-plan", "half-built",
         "remove-one", "new-supplier", "versions-lock", "no-secrets", "two-harbors", "rules-on-the-door",
         "shipyard-in-trouble",
         "harbor-register", "fill-the-blanks", "type-check", "who-wins", "delivery-receipt", "margin-note",
         "order-form",
         "two-ships", "bunk-shift", "fleet-map", "crate",
         "fleet-yard"]
BOSSES = {"shipyard-in-trouble", "order-form", "fleet-yard"}

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
    if "Terraform #" in title:
        title = title.replace("Terraform #", f"Terraform {[x for x in ORDER if x not in BOSSES].index(folder) + 1}")
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
    "🟢 Terraform # · Your first build",
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
    "🔧 Terraform # · Fix the blueprint",
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
    "🟡 Terraform # · References build the order",
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
    "🟢 Terraform # · File layout and fmt",
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
    "🟡 Terraform # · Read the plan",
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
    "🔧 Terraform # · Half built",
    "An apply failed halfway. Finish the job without rebuilding what already stands.",
    f"""
    # Half built

    A storm hit the shipyard: the last `apply` in `/root/halfbuilt` **failed halfway**.
    The ship (`random_pet.ship`) and the dock code (`random_password.dock_code`) were built. The logbook file was not.

    In this lab you will:
    1. Finish a failed apply without rebuilding what already stands
    2. Replace **one** resource on purpose, without touching the code

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
        {"title": "A new dock code",
         "background": """
         cd $R/halfbuilt
         terraform show -json | $PY -c "import json,sys; d=json.load(sys.stdin); print([r['values']['result'] for r in d['values']['root_module']['resources'] if r['address']=='random_password.dock_code'][0])" > /tmp/old_code 2>/dev/null
         md5sum main.tf | cut -d' ' -f1 > /tmp/main_md5
         """,
         "text": """
         The dock code (`random_password.dock_code`) was shouted across the harbor. 🔐
         Get a **new** one: replace that resource, and only that one.

         ⛔ Don't change `main.tf`. ⛔ The ship keeps its name, the logbook stays.
         """,
         "hint": "A plan option forces a replacement without editing the code: `terraform apply -replace=ADDRESS`.",
         "solve": "cd $R/halfbuilt\nterraform apply -replace=random_password.dock_code -auto-approve",
         "wrong": "cd $R/halfbuilt\nsed -i 's/length = 16/length = 17/' main.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/halfbuilt
         [ "$(md5sum main.tf | cut -d' ' -f1)" = "$(cat /tmp/main_md5)" ] || exit 1
         new=$(attr . random_password.dock_code result)
         [ -n "$new" ] && [ "$new" != "$(cat /tmp/old_code)" ] || exit 1
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/pet_id)" ] || exit 1
         st . | grep -qx local_file.logbook || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Terraform has **no rollback**: what succeeded stayed in the state. You fixed the cause and applied again,
    and Terraform only built what was missing. And `-replace=ADDRESS` rebuilt exactly one resource, with no code change.
    """, "Remove one thing"),
    setup=f"""
    mkdir -p $R/halfbuilt && cd $R/halfbuilt
    echo "another crew's notes" > logs
    {hcl("main.tf", '''
    resource "random_pet" "ship" {}

    resource "random_password" "dock_code" {
      length = 16
    }

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
    "🟢 Terraform # · Remove one thing",
    "Retire one resource the everyday way, without destroying the rest.",
    f"""
    # Remove one thing

    In `/root/dismantle` the shipyard manages three parts: `hull`, `mast` and an `old_boat`.
    Next to them lies `neighbor.txt`, made by hand by another shipyard.

    In this lab you will:
    1. Retire one resource the everyday way
    2. Preview a full demolition, saved for review, without demolishing anything

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
        {"title": "Preview the demolition",
         "text": """
         The harbor master wants to **see** what a full teardown would do, before anyone decides.

         Save a **destroy plan** to `/root/dismantle/teardown.tfplan`, and write in `/root/answers/destroy_count.txt`
         how many resources it would destroy.

         ⛔ Don't destroy anything: the hull and the mast must still stand.
         """,
         "hint": "`terraform plan -destroy -out=teardown.tfplan` shows the plan and saves it. Read the summary line.",
         "solve": "cd $R/dismantle\nterraform plan -destroy -out=teardown.tfplan\nmkdir -p $R/answers\necho 2 > $R/answers/destroy_count.txt",
         "wrong": "cd $R/dismantle\nterraform destroy -auto-approve\nmkdir -p $R/answers\necho 2 > $R/answers/destroy_count.txt",
         "verify": """
         cd $R/dismantle
         [ -f teardown.tfplan ] || exit 1
         n=$(terraform show -json teardown.tfplan | $PY -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for r in d.get('resource_changes',[]) if r['change']['actions']==['delete']))")
         [ "$n" = "2" ] || exit 1
         [ "$(tr -d ' \\r\\n' < $R/answers/destroy_count.txt 2>/dev/null)" = "2" ] || exit 1
         s=$(st .)
         echo "$s" | grep -qx local_file.hull && echo "$s" | grep -qx local_file.mast || exit 1
         [ -f hull.txt ] && [ -f mast.txt ] || exit 1
         """},
    ],
    done("""
    Deleting a block and applying is how you retire one resource every day.
    `terraform destroy` removes **everything** in the state, and nothing that isn't in it (like neighbor.txt).
    `plan -destroy -out` lets a team review the teardown first; `terraform apply teardown.tfplan` would run it.
    """, "New supplier"),
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
    "🔧 Terraform # · Versions and the lock file",
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
    """, "No secrets in the blueprint"),
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
    "🟡 Terraform # · Two harbors",
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
    """, "Rules on the door"),
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
    """, "The harbor register"),
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

# ===== Module 3-4 additions (2026-11-04) =================================================================

# new supplier (3.2 init again · 4.1 provider source) ------------------------------------------------------
tf_lab(
    "new-supplier",
    "🔧 Terraform # · New supplier",
    "A new provider in the blueprint: re-run init, and give a non-HashiCorp provider its full source address.",
    f"""
    # New supplier

    The shipyard in `/root/supplier` already builds with the `local` provider. Today the blueprint needs
    **new suppliers**, and Terraform refuses to plan.

    In this lab you will:
    1. See why a new provider means running `init` again
    2. Give a provider from another company its full **source address**

    Lessons: {L("3.2", "terraform init")} · {L("4.1", "How providers work")}
    """,
    [
        {"title": "A new supplier",
         "text": """
         Someone added a `random_pet` to `/root/supplier/main.tf`. Run `terraform plan` and read the error.

         Fix it the right way, then apply: the state must list `random_pet.figurehead`.

         ⛔ Don't delete `.terraform.lock.hcl` or the `.terraform` folder.
         """,
         "hint": "The error says the random provider is *required by this configuration but no version is selected*. Which command downloads providers and records them in the lock file?",
         "solve": "cd $R/supplier\nterraform plan || true\nterraform init\nterraform apply -auto-approve",
         "wrong": "cd $R/supplier\nrm -rf .terraform .terraform.lock.hcl\nterraform init\nterraform apply -auto-approve",
         "verify": """
         cd $R/supplier
         st . | grep -qx random_pet.figurehead || exit 1
         grep -q 'registry.terraform.io/hashicorp/random' .terraform.lock.hcl || exit 1
         [ "$(cat /tmp/supplier_inode)" = "$(stat -c %i .terraform)" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "A supplier from another company",
         "background": """
         cd $R/supplier
         cat > docker.tf <<'HCL'
         resource "docker_image" "harbor_light" {
           name = "nginx:1.27"
         }
         HCL
         """,
         "text": """
         The crew now wants a container image, managed with the **Docker** provider (written by the company
         *kreuzwerker*, not by HashiCorp). See `docker.tf`. `terraform init` fails.

         Read the error, then make `terraform init` and `terraform validate` succeed.
         The lock file must record `kreuzwerker/docker`.

         ⛔ Don't apply: there's no Docker engine in this harbor. `validate` is enough.
         """,
         "hint": "Without a `source`, Terraform guesses `hashicorp/docker`, which doesn't exist. Add a `terraform { required_providers { docker = { source = \"kreuzwerker/docker\" } } }` block.",
         "solve": """cd $R/supplier
terraform init || true
cat > versions.tf <<'HCL'
terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}
HCL
terraform init
terraform validate""",
         "wrong": """cd $R/supplier
cat > versions.tf <<'HCL'
terraform {
  required_providers {
    docker = {
      source = "hashicorp/docker"
    }
  }
}
HCL
terraform init || true""",
         "verify": """
         cd $R/supplier
         grep -q 'registry.terraform.io/kreuzwerker/docker' .terraform.lock.hcl || exit 1
         terraform validate >/dev/null 2>&1 || exit 1
         """},
    ],
    done("""
    `init` is the only command that downloads providers: a new provider in the code means `init` again (the lock
    file gains it, nothing else changes). And only **hashicorp/** providers can skip the source: for every other
    company, write `namespace/type` in `required_providers`.
    """, "Versions and the lock file"),
    setup="""
    mkdir -p $R/supplier && cd $R/supplier
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak hull"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    stat -c %i .terraform > /tmp/supplier_inode
    """ + hcl("figurehead.tf", '''
    resource "random_pet" "figurehead" {}
    '''),
)

# no secrets (4.4) ------------------------------------------------------------------------------------------
tf_lab(
    "no-secrets",
    "🔧 Terraform # · No secrets in the blueprint",
    "A token is hard-coded in a provider block. Move it out of the code.",
    f"""
    # No secrets in the blueprint

    The crew in `/root/secrets` manages its GitHub repositories with the `integrations/github` provider.
    An apprentice pasted a **token** straight into `provider.tf`. That file is about to be pushed to Git,
    and Git never forgets.

    Lesson: {L("4.4", "Configuring a provider")}
    """,
    [
        {"title": "Take the token out",
         "text": """
         Remove the token from every `.tf` file. The provider must keep its **owner** setting, and
         `terraform validate` must still succeed.

         Then write in `/root/answers/token_env.txt` the name of the **environment variable** the GitHub provider
         reads its token from, so the crew can set it in their terminal or pipeline instead.
         """,
         "hint": "Delete the `token = ...` line, keep `owner`. The provider's docs (and its error messages) name the variable: `GITHUB_TOKEN`.",
         "solve": "cd $R/secrets\nsed -i '/token *=/d' provider.tf\nterraform validate\nmkdir -p $R/answers\necho GITHUB_TOKEN > $R/answers/token_env.txt",
         "wrong": """cd $R/secrets
sed -i 's/token *= *"ghp_[A-Za-z0-9]*"/token = var.github_token/' provider.tf
cat > variables.tf <<'HCL'
variable "github_token" {
  default = "ghp_SHIPYARD0000000000000000000000000000"
}
HCL
mkdir -p $R/answers
echo GITHUB_TOKEN > $R/answers/token_env.txt""",
         "verify": """
         cd $R/secrets
         ! grep -rqs 'ghp_' --include='*.tf' --include='*.tfvars' . || exit 1
         ! grep -q 'token *=' provider.tf || exit 1
         grep -q 'owner *= *"captain-kube"' provider.tf || exit 1
         terraform validate >/dev/null 2>&1 || exit 1
         [ "$(tr -d ' \\r\\n' < $R/answers/token_env.txt 2>/dev/null)" = "GITHUB_TOKEN" ] || exit 1
         """},
    ],
    done("""
    The provider block keeps **where** (owner, region, profile). **Who** you are comes from the environment:
    `export GITHUB_TOKEN=...` on a laptop, a secret or a short-lived role in the pipeline. A default in a variable
    is still code, and still ends up in Git.
    """, "Two harbors"),
    setup="""
    mkdir -p $R/secrets && cd $R/secrets
    """ + hcl("provider.tf", '''
    terraform {
      required_providers {
        github = {
          source = "integrations/github"
        }
      }
    }

    provider "github" {
      owner = "captain-kube"
      token = "ghp_SHIPYARD0000000000000000000000000000"
    }
    ''') + hcl("main.tf", '''
    resource "github_repository" "logbook" {
      name       = "harbor-logbook"
      visibility = "private"
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# rules on the door (4.6 the terraform block) ----------------------------------------------------------------
tf_lab(
    "rules-on-the-door",
    "🔧 Terraform # · Rules on the door",
    "The terraform block: a required_version nobody can meet, and a variable where only fixed values go.",
    f"""
    # Rules on the door

    The `terraform {{ }}` block in `/root/rules` holds the shipyard's rules: which Terraform, which suppliers,
    where the ledger is kept. Two of them are broken, and `terraform init` won't even start.

    Lesson: {L("4.6", "The terraform block")}
    """,
    [
        {"title": "The right Terraform",
         "text": """
         Run `terraform init` in `/root/rules` and read the first error.

         Fix it so this Terraform (1.12) is accepted, **keeping** a `required_version` rule that allows 1.12.x.
         For now, `init` may still fail with a second error: that's the next step.
         """,
         "hint": "`terraform version` shows what you run. `required_version = \"~> 1.12\"` allows 1.12 and newer 1.x.",
         "solve": "cd $R/rules\nterraform init || true\nsed -i 's/required_version = \">= 1.13\"/required_version = \"~> 1.12\"/' terraform.tf",
         "wrong": "cd $R/rules\nsed -i '/required_version/d' terraform.tf",
         "verify": """
         cd $R/rules
         grep -q 'required_version' terraform.tf || exit 1
         ! grep -q '>= 1.13' terraform.tf || exit 1
         ! terraform init -input=false -backend=false 2>&1 | grep -q 'Unsupported Terraform Core version' || exit 1
         """},
        {"title": "Fixed values only",
         "text": """
         Now `init` complains about the **backend**. Fix it so the ledger is kept at
         `/root/rules/ledger/shipyard.tfstate`, then `init` and `apply`.

         ⛔ Keep the `local` backend and its `path`. ⛔ The variable `state_path` may stay, but the backend can't use it.
         """,
         "hint": "The terraform block is read before any variable exists: `Variables may not be used here`. Write the path as a fixed string.",
         "solve": "cd $R/rules\nsed -i 's#path = var.state_path#path = \"ledger/shipyard.tfstate\"#' terraform.tf\nterraform init\nterraform apply -auto-approve",
         "wrong": "cd $R/rules\nsed -i '/backend \"local\"/,/}/d' terraform.tf\nterraform init\nterraform apply -auto-approve",
         "verify": """
         cd $R/rules
         grep -q 'backend "local"' terraform.tf || exit 1
         ! grep -q 'var\\.' terraform.tf || exit 1
         [ -f ledger/shipyard.tfstate ] || exit 1
         grep -q '"local_file"' ledger/shipyard.tfstate || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    The terraform block is read **first**, before variables and locals exist, so it only takes fixed values:
    `required_version`, `required_providers`, and `backend` (or `cloud`). Per-environment backend settings come
    from `terraform init -backend-config=...` (Module 8).
    """, "BOSS · Shipyard in trouble"),
    setup="""
    mkdir -p $R/rules && cd $R/rules
    """ + hcl("terraform.tf", '''
    terraform {
      required_version = ">= 1.13"

      backend "local" {
        path = var.state_path
      }
    }
    ''') + hcl("variables.tf", '''
    variable "state_path" {
      type    = string
      default = "ledger/shipyard.tfstate"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "rules" {
      filename = "${path.module}/rules.txt"
      content  = "One quill at a time."
    }
    '''),
)

# ===== Module 5 · Configuration (2026-11-04) ===============================================================

# harbor register (5.1 resource vs data · 5.2 attributes) -------------------------------------------------
tf_lab(
    "harbor-register",
    "🔧 Terraform # · The harbor register",
    "Read an existing file with a data block instead of managing it, then use a computed attribute.",
    f"""
    # The harbor register

    In `/root/register`, the harbor master keeps `ships.txt` **by hand**. It isn't ours: we may read it,
    never write it. An apprentice wanted a banner with the register in capitals... and wrote a **resource** for it.

    In this lab you will:
    1. Read the register with a **data** block
    2. Use an attribute that's only **known after apply**

    Lessons: {L("5.1", "Resource vs data")} · {L("5.2", "Arguments and attributes")}
    """,
    [
        {"title": "Read, don't build",
         "text": """
         Run `terraform plan` in `/root/register` and look at what it would do to `ships.txt`. 😱

         Fix the blueprint so that `banner.txt` holds the register **in capitals**, by **reading** `ships.txt`.

         ⛔ `ships.txt` must not change, and must not be managed by Terraform (no `local_file.register` in the state).
         """,
         "hint": "Replace the `resource \"local_file\" \"register\"` block with `data \"local_file\" \"register\" { filename = ... }` (no content), and reference it as `data.local_file.register.content`.",
         "solve": """cd $R/register
$PY - <<'PY'
import re
p='main.tf'; t=open(p).read()
t=re.sub(r'resource "local_file" "register" \\{.*?\\n\\}', 'data "local_file" "register" {\\n  filename = "${path.module}/ships.txt"\\n}', t, flags=re.S)
t=t.replace('local_file.register.content', 'data.local_file.register.content')
open(p,'w').write(t)
PY
terraform apply -auto-approve""",
         "wrong": """cd $R/register
sed -i 's#content  = ""#content  = file("${path.module}/ships.txt")#' main.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/register
         [ "$(md5sum ships.txt | cut -d' ' -f1)" = "$(cat /tmp/ships_md5)" ] || exit 1
         s=$(st .)
         echo "$s" | grep -qx data.local_file.register || exit 1
         ! echo "$s" | grep -qx local_file.register || exit 1
         $PY -c "import sys; sys.exit(open('banner.txt').read()!=open('ships.txt').read().upper())" || exit 1
         noplan . || exit 1
         """},
        {"title": "Known after apply",
         "text": """
         Every ship needs a captain. Add to `main.tf`:
         - a `random_pet` called `captain`
         - a `local_file` called `captain` that writes `captain.txt` with exactly **`Captain: <the pet's id>`**

         **Before** you apply, run `terraform plan` and write in `/root/answers/known.txt` the name of the
         `random_pet.captain` attribute that shows **(known after apply)**. Then apply.
         """,
         "hint": "Reference it as `random_pet.captain.id`. In the plan, `length` and `separator` are known, the id isn't yet.",
         "solve": """cd $R/register
cat >> main.tf <<'HCL'

resource "random_pet" "captain" {}

resource "local_file" "captain" {
  filename = "${path.module}/captain.txt"
  content  = "Captain: ${random_pet.captain.id}"
}
HCL
terraform init
terraform plan
mkdir -p $R/answers
echo id > $R/answers/known.txt
terraform apply -auto-approve""",
         "wrong": """cd $R/register
cat >> main.tf <<'HCL'

resource "random_pet" "captain" {}

resource "local_file" "captain" {
  filename = "${path.module}/captain.txt"
  content  = "Captain: Kestrel"
}
HCL
terraform init
mkdir -p $R/answers
echo length > $R/answers/known.txt
terraform apply -auto-approve""",
         "verify": """
         cd $R/register
         [ "$(tr -d ' \\r\\n' < $R/answers/known.txt 2>/dev/null)" = "id" ] || exit 1
         id=$(attr . random_pet.captain id)
         [ -n "$id" ] || exit 1
         [ "$(cat captain.txt 2>/dev/null)" = "Captain: $id" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A **resource** is built and owned: Terraform would have overwritten the register. A **data** source only reads
    (`data.TYPE.NAME`), and it lands in the state as a read, not as something to manage. And computed attributes
    like `id` are filled in during apply: references carry them along.
    """, "Fill the blanks"),
    setup="""
    mkdir -p $R/register && cd $R/register
    printf 'Kestrel\\nOsprey\\nPetrel\\n' > ships.txt
    md5sum ships.txt | cut -d' ' -f1 > /tmp/ships_md5
    """ + hcl("main.tf", '''
    # the apprentice's idea: manage the register to read it
    resource "local_file" "register" {
      filename = "${path.module}/ships.txt"
      content  = ""
    }

    resource "local_file" "banner" {
      filename = "${path.module}/banner.txt"
      content  = upper(local_file.register.content)
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# fill the blanks (5.3 input variables) -------------------------------------------------------------------
tf_lab(
    "fill-the-blanks",
    "🟢 Terraform # · Fill the blanks",
    "Turn hard-coded names into a typed input variable, then fix a value of the wrong type.",
    f"""
    # Fill the blanks

    The blueprint in `/root/blanks` was drawn for one customer: the name **Kestrel** is written in it twice.
    Today's customer ordered the **Osprey**. Time to draw blanks instead.

    Lesson: {L("5.3", "Input variables")}
    """,
    [
        {"title": "Draw a blank",
         "text": """
         In `/root/blanks`:
         1. Declare a variable `ship_name` in `variables.tf`, with `type = string`, a `description`, and **no default**
         2. Use it in both files instead of `Kestrel`
         3. Put `ship_name = "Osprey"` in `terraform.tfvars`, then apply

         `hull.txt` must say `Hull of the Osprey`, `flag.txt` must say `Flag of the Osprey`.
         """,
         "hint": "`variable \"ship_name\" { type = string  description = \"...\" }` and `\"Hull of the ${var.ship_name}\"`. terraform.tfvars is loaded automatically.",
         "solve": """cd $R/blanks
cat > variables.tf <<'HCL'
variable "ship_name" {
  type        = string
  description = "Name of the ship on the order"
}
HCL
sed -i 's/Kestrel/${var.ship_name}/' main.tf
echo 'ship_name = "Osprey"' > terraform.tfvars
terraform apply -auto-approve""",
         "wrong": """cd $R/blanks
sed -i 's/Kestrel/Osprey/' main.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/blanks
         $PY - <<'PY' || exit 1
import re,sys
t=open('variables.tf').read()
m=re.search(r'variable\\s+"ship_name"\\s*\\{(.*?)\\n\\}', t, re.S)
ok = m and re.search(r'type\\s*=\\s*string', m.group(1)) and 'description' in m.group(1) and 'default' not in m.group(1)
sys.exit(0 if ok else 1)
PY
         ! grep -q 'Kestrel\\|Osprey' main.tf || exit 1
         [ "$(grep -c 'var.ship_name' main.tf)" -ge 2 ] || exit 1
         [ "$(cat hull.txt)" = "Hull of the Osprey" ] && [ "$(cat flag.txt)" = "Flag of the Osprey" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "The wrong kind of value",
         "background": """
         cd $R/blanks
         cat >> variables.tf <<'HCL'

         variable "masts" {
           type        = number
           description = "How many masts"
         }
         HCL
         cat >> main.tf <<'HCL'

         resource "local_file" "masts" {
           filename = "${path.module}/masts.txt"
           content  = "${var.masts} masts"
         }
         HCL
         echo 'masts = "three"' >> terraform.tfvars
         sed -i 's/^         //' variables.tf main.tf
         """,
         "text": """
         The customer also ordered masts. Someone added a `masts` variable (a **number**) and filled in the order...
         Run `terraform plan` and read the error.

         Fix it so `masts.txt` says `3 masts`. ⛔ `masts` must stay a `number`.
         """,
         "hint": "`a number is required`: the order says `\"three\"`. Write the value as a number in terraform.tfvars: `masts = 3`.",
         "solve": "cd $R/blanks\nterraform plan || true\nsed -i 's/masts = \"three\"/masts = 3/' terraform.tfvars\nterraform apply -auto-approve",
         "wrong": "cd $R/blanks\nsed -i 's/type        = number/type        = string/' variables.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/blanks
         $PY - <<'PY' || exit 1
import re,sys
t=open('variables.tf').read()
m=re.search(r'variable\\s+"masts"\\s*\\{(.*?)\\n\\}', t, re.S)
sys.exit(0 if m and re.search(r'type\\s*=\\s*number', m.group(1)) else 1)
PY
         [ "$(cat masts.txt)" = "3 masts" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A variable is a blank in the blueprint: declared with a type and a description, used as `var.name`, filled from
    terraform.tfvars, -var or the environment. The type is a promise: a wrong value is caught **before** anything
    is built, and you fix the value, not the promise.
    """, "Type check"),
    setup="""
    mkdir -p $R/blanks && cd $R/blanks
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "Hull of the Kestrel"
    }

    resource "local_file" "flag" {
      filename = "${path.module}/flag.txt"
      content  = "Flag of the Kestrel"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# type check (5.4 collections · 5.5 objects) ---------------------------------------------------------------
tf_lab(
    "type-check",
    "🔧 Terraform # · Type check",
    "A set that can't be indexed, and an object order that leaves out an attribute.",
    f"""
    # Type check

    In `/root/types` the crew declared its inputs with careful types... a little too careful.

    In this lab you will:
    1. Fix a **set** used like a list
    2. Make an **object** attribute optional, with a default

    Lessons: {L("5.4", "Simple and collection types")} · {L("5.5", "Objects and tuples")}
    """,
    [
        {"title": "The first wood",
         "text": """
         `keel.txt` must hold the **first** wood of `woods`, in the order it's written (`oak`), and the list must keep
         every entry, duplicates included. Run `terraform plan`, read the error, fix the blueprint, apply.

         ⛔ Keep reading the value from `var.woods` (no hard-coded `"oak"`).
         """,
         "hint": "`Elements of a set are identified only by their value and don't have any separate index or key`. A **list** keeps order and duplicates: `type = list(string)`.",
         "solve": "cd $R/types\nterraform plan || true\nsed -i 's/type    = set(string)/type    = list(string)/' variables.tf\nterraform apply -auto-approve",
         "wrong": "cd $R/types\nsed -i 's/content  = var.woods\\[0\\]/content  = \"oak\"/' main.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/types
         grep -q 'var.woods' main.tf || exit 1
         grep -q 'list(string)' variables.tf || exit 1
         [ "$(cat keel.txt 2>/dev/null)" = "oak" ] || exit 1
         [ "$(echo 'length(var.woods)' | terraform console 2>/dev/null)" = "3" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "An optional flag",
         "background": """
         cd $R/types
         cat >> variables.tf <<'HCL'

         variable "ship" {
           type = object({ name = string, masts = number, flag = string })
         }
         HCL
         cat > terraform.tfvars <<'HCL'
         ship = {
           name  = "Kestrel"
           masts = 2
         }
         HCL
         cat >> main.tf <<'HCL'

         resource "local_file" "flag" {
           filename = "${path.module}/flag.txt"
           content  = "${var.ship.name} flies ${var.ship.flag}"
         }
         HCL
         sed -i 's/^         //' variables.tf main.tf terraform.tfvars
         md5sum terraform.tfvars | cut -d' ' -f1 > /tmp/order_md5
         """,
         "text": """
         The order in `terraform.tfvars` describes the ship with an **object**, but doesn't say the flag.
         Run `terraform plan` and read the error.

         Most customers don't care about the flag: make it **optional, violet by default**.
         `flag.txt` must say `Kestrel flies violet`.

         ⛔ Don't change `terraform.tfvars`: that's the customer's order.
         """,
         "hint": "In the object type: `flag = optional(string, \"violet\")`. The second argument is the default.",
         "solve": "cd $R/types\nterraform plan || true\nsed -i 's/flag = string/flag = optional(string, \"violet\")/' variables.tf\nterraform apply -auto-approve",
         "wrong": "cd $R/types\nsed -i 's/masts = 2/masts = 2\\n  flag  = \"violet\"/' terraform.tfvars\nterraform apply -auto-approve",
         "verify": """
         cd $R/types
         [ "$(md5sum terraform.tfvars | cut -d' ' -f1)" = "$(cat /tmp/order_md5)" ] || exit 1
         grep -q 'optional(string, *"violet")' variables.tf || exit 1
         [ "$(cat flag.txt 2>/dev/null)" = "Kestrel flies violet" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A **set** keeps unique values and has no positions; a **list** keeps order and duplicates. An **object** fixes
    named attributes with their own types, and `optional(type, default)` lets the caller leave one out.
    """, "Who wins?"),
    setup="""
    mkdir -p $R/types && cd $R/types
    """ + hcl("variables.tf", '''
    variable "woods" {
      type    = set(string)
      default = ["oak", "pine", "oak"]
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "keel" {
      filename = "${path.module}/keel.txt"
      content  = var.woods[0]
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# who wins (5.6 precedence) ----------------------------------------------------------------------------------
tf_lab(
    "who-wins",
    "🟡 Terraform # · Who wins?",
    "The same variable set in five places: predict the winner, then make the right file win.",
    f"""
    # Who wins?

    In `/root/wins` the variable `flag` is set in **five** places: its default, `terraform.tfvars`,
    `a.auto.tfvars`, `z.auto.tfvars` and `prod.tfvars`. Look at each file first.

    Lesson: {L("5.6", "Setting values: who wins?")}
    """,
    [
        {"title": "Predict",
         "text": """
         Without changing anything: which value does `var.flag` get when you run a plain `terraform plan`?
         Write it in `/root/answers/winner.txt`.

         You may check yourself with `echo var.flag | terraform console`.
         """,
         "hint": "Later sources win: default → environment → terraform.tfvars → *.auto.tfvars (alphabetical) → -var / -var-file. Which files load on their own?",
         "solve": "cd $R/wins\necho var.flag | terraform console\nmkdir -p $R/answers\necho z-auto > $R/answers/winner.txt",
         "wrong": "mkdir -p $R/answers\necho tfvars > $R/answers/winner.txt",
         "verify": """
         [ "$(tr -d ' \\r\\n' < $R/answers/winner.txt 2>/dev/null)" = "z-auto" ] || exit 1
         """},
        {"title": "Make prod win",
         "text": """
         Apply so that `flag.txt` says **prod**.

         ⛔ Don't edit, rename or delete any `.tf` or `.tfvars` file, and don't create new ones.
         """,
         "hint": "prod.tfvars never loads on its own. Pass it on the command line: `terraform apply -var-file=prod.tfvars`.",
         "solve": "cd $R/wins\nterraform apply -var-file=prod.tfvars -auto-approve",
         "wrong": "cd $R/wins\ncp prod.tfvars zz.auto.tfvars\nterraform apply -auto-approve",
         "verify": """
         cd $R/wins
         md5sum -c /tmp/wins_md5 >/dev/null 2>&1 || exit 1
         [ "$(ls *.tf *.tfvars | wc -l)" = "6" ] || exit 1
         [ "$(cat flag.txt 2>/dev/null)" = "prod" ] || exit 1
         [ "$(attr . local_file.flag content)" = "prod" ] || exit 1
         """},
        {"title": "Two flags on one line",
         "text": """
         Last question, no apply needed. What does `var.flag` become with:

         ```
         terraform plan -var 'flag=cli' -var-file=prod.tfvars
         ```

         Write the value in `/root/answers/order.txt`.
         """,
         "hint": "On the command line, flags are read in the order you type them: the last one wins.",
         "solve": "mkdir -p $R/answers\necho prod > $R/answers/order.txt",
         "wrong": "mkdir -p $R/answers\necho cli > $R/answers/order.txt",
         "verify": """
         [ "$(tr -d ' \\r\\n' < $R/answers/order.txt 2>/dev/null)" = "prod" ] || exit 1
         """},
    ],
    done("""
    default → `TF_VAR_flag` → terraform.tfvars → `*.auto.tfvars` (z beats a) → `-var` / `-var-file` in the order
    typed. Other `.tfvars` files only load with `-var-file`: that's how one blueprint serves dev and prod.
    """, "Delivery receipt"),
    setup="""
    mkdir -p $R/wins && cd $R/wins
    """ + hcl("variables.tf", '''
    variable "flag" {
      type    = string
      default = "default"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "flag" {
      filename = "${path.module}/flag.txt"
      content  = var.flag
    }
    ''') + """
    echo 'flag = "tfvars"' > terraform.tfvars
    echo 'flag = "a-auto"' > a.auto.tfvars
    echo 'flag = "z-auto"' > z.auto.tfvars
    echo 'flag = "prod"' > prod.tfvars
    md5sum *.tf *.tfvars > /tmp/wins_md5
    terraform init -input=false >/dev/null
    """,
)

# delivery receipt (5.7 outputs) -------------------------------------------------------------------------------
tf_lab(
    "delivery-receipt",
    "🔧 Terraform # · Delivery receipt",
    "Fix a sensitive output, add a new one, and read an output the way scripts do.",
    f"""
    # Delivery receipt

    When a ship leaves `/root/receipt`, the customer gets a receipt: the ship's name and the dock code.
    But `terraform plan` refuses to run.

    Lesson: {L("5.7", "Output values")}
    """,
    [
        {"title": "Fix the receipt",
         "text": """
         Read the error from `terraform plan`, then fix `outputs.tf`:
         - `dock_code` stays an output, but must never print on the screen
         - add an output `ship_name` with the pet's id

         Apply. `terraform output` must show `dock_code = <sensitive>` and the ship's name.
         """,
         "hint": "`Output refers to sensitive values`: random_password's result is sensitive. Add `sensitive = true` to the dock_code output.",
         "solve": """cd $R/receipt
cat > outputs.tf <<'HCL'
output "dock_code" {
  value     = random_password.dock_code.result
  sensitive = true
}

output "ship_name" {
  value = random_pet.ship.id
}
HCL
terraform apply -auto-approve
terraform output""",
         "wrong": """cd $R/receipt
cat > outputs.tf <<'HCL'
output "ship_name" {
  value = random_pet.ship.id
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/receipt
         terraform output -json 2>/dev/null | $PY -c "
import json,sys
o=json.load(sys.stdin)
ok = o.get('dock_code',{}).get('sensitive') is True and 'ship_name' in o and not o['ship_name']['sensitive']
sys.exit(0 if ok else 1)" || exit 1
         [ "$(terraform output -raw ship_name)" = "$(attr . random_pet.ship id)" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "For the script",
         "text": """
         A harbor script needs the ship's name in `/root/receipt/name.txt`: **just the name**,
         no quotes. Get it from `terraform output`.
         """,
         "hint": "`terraform output ship_name` prints it in quotes. `-raw` prints the plain string, ready for scripts.",
         "solve": "cd $R/receipt\nterraform output -raw ship_name > name.txt",
         "wrong": "cd $R/receipt\nterraform output ship_name > name.txt",
         "verify": """
         cd $R/receipt
         [ "$(tr -d '\\r\\n' < name.txt 2>/dev/null)" = "$(attr . random_pet.ship id)" ] || exit 1
         """},
    ],
    done("""
    Outputs are the delivery receipt. `-raw` for scripts, `-json` for tools. `sensitive = true` hides a value from
    the screen, but asking for it by name, `-json` and `-raw` still print it, and the state keeps it in plain text.
    """, "Margin note"),
    setup="""
    mkdir -p $R/receipt && cd $R/receipt
    """ + hcl("main.tf", '''
    resource "random_pet" "ship" {}

    resource "random_password" "dock_code" {
      length = 12
    }
    ''') + hcl("outputs.tf", '''
    output "dock_code" {
      value = random_password.dock_code.result
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# margin note (5.8 locals) --------------------------------------------------------------------------------------
tf_lab(
    "margin-note",
    "🟡 Terraform # · Margin note",
    "Name a repeated expression once with locals, without changing what's built.",
    f"""
    # Margin note

    The blueprint in `/root/margin` writes `shipyard-${{var.env}}` in **six** places. One typo, and one file lands
    in the wrong place. Time for a note in the margin.

    Lesson: {L("5.8", "Locals")}
    """,
    [
        {"title": "Write it once",
         "text": """
         Add a `locals` block with `prefix = "shipyard-${var.env}"`, and use `local.prefix` everywhere instead.

         This is a **refactor**: nothing real may change. After your edit, `terraform plan` must say **No changes**.
         """,
         "hint": "`locals { prefix = \"shipyard-${var.env}\" }` (block: locals, plural) and `\"${local.prefix}-hull.txt\"` (reference: local, singular).",
         "solve": """cd $R/margin
$PY - <<'PY'
p='main.tf'; t=open(p).read()
t=t.replace('shipyard-${var.env}', '${local.prefix}')
t='locals {\\n  prefix = "shipyard-${var.env}"\\n}\\n\\n'+t
open(p,'w').write(t)
PY
terraform plan""",
         "wrong": """cd $R/margin
$PY - <<'PY'
p='main.tf'; t=open(p).read()
t=t.replace('shipyard-${var.env}', '${local.prefix}')
t='locals {\\n  prefix = "shipyard_${var.env}"\\n}\\n\\n'+t
open(p,'w').write(t)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/margin
         [ "$(grep -o 'shipyard-' main.tf | wc -l)" = "1" ] || exit 1
         [ "$(grep -o 'local\\.prefix' main.tf | wc -l)" -ge 6 ] || exit 1
         grep -q '^locals' main.tf || exit 1
         noplan . || exit 1
         """},
        {"title": "Sail to prod",
         "background": """
         cd $R/margin
         md5sum *.tf > /tmp/margin_md5
         """,
         "text": """
         The same blueprint must now build the **prod** shipyard: every file named `shipyard-prod-...`.

         ⛔ Don't edit any `.tf` file. Locals can't be set from outside... but what are they built from?
         """,
         "hint": "`local.prefix` is built from `var.env`, and a variable *can* come from outside: `terraform apply -var 'env=prod'`.",
         "solve": "cd $R/margin\nterraform apply -var 'env=prod' -auto-approve",
         "wrong": "cd $R/margin\nsed -i 's/default = \"dev\"/default = \"prod\"/' variables.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/margin
         md5sum -c /tmp/margin_md5 >/dev/null 2>&1 || exit 1
         [ -f shipyard-prod-hull.txt ] && [ -f shipyard-prod-mast.txt ] && [ -f shipyard-prod-sail.txt ] || exit 1
         [ ! -f shipyard-dev-hull.txt ] || exit 1
         """},
    ],
    done("""
    `locals {}` (plural) names an expression once; `local.name` (singular) uses it. Locals are set only inside the
    configuration, but they can be built from variables: change the input, and every use follows.
    """, "BOSS · The order form"),
    setup="""
    mkdir -p $R/margin && cd $R/margin
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "dev"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/shipyard-${var.env}-hull.txt"
      content  = "shipyard-${var.env} hull"
    }

    resource "local_file" "mast" {
      filename = "${path.module}/shipyard-${var.env}-mast.txt"
      content  = "shipyard-${var.env} mast"
    }

    resource "local_file" "sail" {
      filename = "${path.module}/shipyard-${var.env}-sail.txt"
      content  = "shipyard-${var.env} sail"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# boss (5.R) ------------------------------------------------------------------------------------------------------
tf_lab(
    "order-form",
    "🔴 Terraform BOSS · The order form",
    "Five configuration faults hidden in one order form. Only the goal is given.",
    f"""
    # 🔴 BOSS · The order form

    The order form in `/root/order` won't even plan, and the crew list next to it is in danger.
    You only get the **goal**.

    Covers Module 5: {L("5.1", "data")} · {L("5.4", "types")} · {L("5.5", "objects")} · {L("5.7", "outputs")} · {L("5.8", "locals")}
    """,
    [
        {"title": "Fill the order",
         "text": """
         In `/root/order`, reach this state:
         - `terraform validate` says Success and `terraform plan` says **No changes**
         - `crew.txt` is **read**, never managed or changed (it's the harbor master's list)
         - `manifest.txt` says exactly:
           ```
           prod-Kestrel: 2 masts, flag violet
           crew: <the content of crew.txt>
           ```
         - `terraform output -raw label` prints `prod-Kestrel`
         - `dock_code` is an output that never shows on the screen

         ⛔ Customers don't always say the flag: it must default to **violet**.
         """,
         "hint": "Go error by error: validate, then plan. Look for: a resource that should be a data source, a reference with the wrong prefix, a value of the wrong type, an object attribute that should be optional, a sensitive output.",
         "solve": """cd $R/order
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'resource "local_file" "crew" \\{.*?\\n\\}', 'data "local_file" "crew" {\\n  filename = "${path.module}/crew.txt"\\n}', t, flags=re.S)
t=t.replace('local_file.crew.content','data.local_file.crew.content').replace('locals.label','local.label')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('flag = string','flag = optional(string, "violet")')
open('variables.tf','w').write(v)
o=open('terraform.tfvars').read().replace('masts = "two"','masts = 2')
open('terraform.tfvars','w').write(o)
out=open('outputs.tf').read().replace('value = random_password.dock_code.result','value     = random_password.dock_code.result\\n  sensitive = true')
open('outputs.tf','w').write(out)
PY
terraform fmt
terraform validate
terraform apply -auto-approve""",
         "wrong": """cd $R/order
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('content  = ""','content  = file("${path.module}/crew.txt")').replace('locals.label','local.label')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('flag = string','flag = optional(string, "violet")')
open('variables.tf','w').write(v)
o=open('terraform.tfvars').read().replace('masts = "two"','masts = 2')
open('terraform.tfvars','w').write(o)
out=open('outputs.tf').read().replace('value = random_password.dock_code.result','value     = random_password.dock_code.result\\n  sensitive = true')
open('outputs.tf','w').write(out)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/order
         terraform validate >/dev/null 2>&1 || exit 1
         [ "$(md5sum crew.txt | cut -d' ' -f1)" = "$(cat /tmp/crew_md5)" ] || exit 1
         s=$(st .)
         echo "$s" | grep -qx data.local_file.crew || exit 1
         ! echo "$s" | grep -qx local_file.crew || exit 1
         $PY -c "import sys; sys.exit(open('manifest.txt').read()!='prod-Kestrel: 2 masts, flag violet\\ncrew: '+open('crew.txt').read())" || exit 1
         [ "$(terraform output -raw label 2>/dev/null)" = "prod-Kestrel" ] || exit 1
         terraform output -json | $PY -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('dock_code',{}).get('sensitive') is True else 1)" || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Data instead of a resource, `local.` not `locals.`, a number where a number was promised, an optional object
    attribute and a sensitive output: the whole of Module 5 in one order form. ⚒
    """),
    setup="""
    mkdir -p $R/order && cd $R/order
    printf 'Ada\\nBo\\nCyrus\\n' > crew.txt
    md5sum crew.txt | cut -d' ' -f1 > /tmp/crew_md5
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "prod"
    }

    variable "ship" {
      type = object({ name = string, masts = number, flag = string })
    }
    ''') + hcl("terraform.tfvars", '''
    ship = {
      name  = "Kestrel"
      masts = "two"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "crew" {
      filename = "${path.module}/crew.txt"
      content  = ""
    }

    locals {
      label = "${var.env}-${var.ship.name}"
    }

    resource "local_file" "manifest" {
      filename = "${path.module}/manifest.txt"
      content  = "${locals.label}: ${var.ship.masts} masts, flag ${var.ship.flag}\\ncrew: ${local_file.crew.content}"
    }

    resource "random_password" "dock_code" {
      length = 12
    }
    ''') + hcl("outputs.tf", '''
    output "label" {
      value = local.label
    }

    output "dock_code" {
      value = random_password.dock_code.result
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# 6.1 + 6.2 · conditionals and functions ---------------------------------------------------------------------------
tf_lab(
    "two-ships",
    "🟢 Terraform # · Two ships, one blueprint",
    "A conditional for dev and prod, then built-in functions in a local.",
    f"""
    # Two ships, one blueprint

    The blueprint in `/root/two` builds a ship file. Dev ships get **one** mast, prod ships need **three**,
    and right now the number is written by hand.

    Lessons: {L("6.1", "Expressions and conditionals")} · {L("6.2", "Built-in functions")}
    """,
    [
        {"title": "Masts by environment",
         "text": """
         Change `local.masts` so it is **3 in prod** and **1 everywhere else**, then build prod:

         ```
         terraform apply -var env=prod
         ```

         `ship.txt` must say `Kestrel (prod) masts: 3`, and the same blueprint must still give 1 mast in dev.

         💡 Try your expression first in `terraform console`.
         """,
         "hint": "condition ? value_if_true : value_if_false. Compare with `==`: `var.env == \"prod\" ? 3 : 1`.",
         "solve": """cd $R/two
sed -i 's/masts = 1/masts = var.env == "prod" ? 3 : 1/' main.tf
terraform apply -var env=prod -auto-approve""",
         "wrong": """cd $R/two
sed -i 's/masts = 1/masts = 3/' main.tf
terraform apply -var env=prod -auto-approve""",
         "verify": """
         cd $R/two
         [ "$(attr . local_file.ship content)" = "Kestrel (prod) masts: 3" ] || exit 1
         [ "$(echo 'local.masts' | terraform console -var env=dev 2>/dev/null)" = "1" ] || exit 1
         [ "$(echo 'local.masts' | terraform console -var env=staging 2>/dev/null)" = "1" ] || exit 1
         """},
        {"title": "The dock code",
         "text": """
         The output `dock_code` prints `dock-7`. The harbor wants **`DOCK-007`**: capitals, and the number padded
         to three digits.

         Build it in a local named **`dock_code`** from `var.yard` and `var.dock_number`, output that local, and apply.
         With `dock_number = 42` it must give `DOCK-042`.

         ⛔ Terraform has no functions of your own: combine the built-in ones.
         """,
         "hint": "`format(\"%s-%03d\", var.yard, var.dock_number)` pads the number; wrap it in `upper(...)`. Test it: `terraform console -var dock_number=42`, then `local.dock_code`.",
         "solve": """cd $R/two
cat >> main.tf <<'HCL'

locals {
  dock_code = upper(format("%s-%03d", var.yard, var.dock_number))
}
HCL
sed -i 's|value = .*|value = local.dock_code|' outputs.tf
terraform apply -var env=prod -auto-approve
terraform output -raw dock_code""",
         "wrong": """cd $R/two
cat >> main.tf <<'HCL'

locals {
  dock_code = "DOCK-007"
}
HCL
sed -i 's|value = .*|value = local.dock_code|' outputs.tf
terraform apply -var env=prod -auto-approve""",
         "verify": """
         cd $R/two
         [ "$(terraform output -raw dock_code 2>/dev/null)" = "DOCK-007" ] || exit 1
         [ "$(echo 'local.dock_code' | terraform console -var dock_number=42 2>/dev/null)" = '"DOCK-042"' ] || exit 1
         """},
    ],
    done("""
    `cond ? a : b` picks a value per environment, and both sides must have the same type. Functions are built in
    only: you combine them (`upper(format(...))`) and name the result with a local. `terraform console` is the
    place to try them.
    """, "Terraform · The bunk shift"),
    setup="""
    mkdir -p $R/two && cd $R/two
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "dev"
    }

    variable "ship" {
      type    = string
      default = "Kestrel"
    }

    variable "yard" {
      type    = string
      default = "dock"
    }

    variable "dock_number" {
      type    = number
      default = 7
    }
    ''') + hcl("main.tf", '''
    locals {
      masts = 1
    }

    resource "local_file" "ship" {
      filename = "${path.module}/ship.txt"
      content  = "${var.ship} (${var.env}) masts: ${local.masts}"
    }
    ''') + hcl("outputs.tf", '''
    output "dock_code" {
      value = "${var.yard}-${var.dock_number}"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 6.3 + 6.4 · count -> for_each -------------------------------------------------------------------------------------
tf_lab(
    "bunk-shift",
    "🟡 Terraform # · The bunk shift",
    "Move numbered count copies to named for_each instances, then remove one crew member safely.",
    f"""
    # The bunk shift

    In `/root/bunks`, one `local_file.bunk` per crew member is built with **count**: `bunk[0]`, `bunk[1]`, `bunk[2]`.
    Bo is leaving at the next port.

    See the problem first (this changes nothing):
    ```
    cd /root/bunks
    terraform plan -var 'crew=["Ada","Cyrus"]'
    ```
    One person leaves, and two bunks change. 😬

    Lessons: {L("6.3", "count")} · {L("6.4", "for_each")}
    """,
    [
        {"title": "Name plates",
         "text": """
         Switch the bunks from `count` to **for_each**, so each bunk is keyed by its crew member's name:

         - addresses `local_file.bunk["Ada"]`, `["Bo"]`, `["Cyrus"]`
         - file `bunk-<name>.txt` containing `Bunk of <name>`

         Apply it. Moving from count to for_each rebuilds the bunks once; that's fine here (Module 9 shows `moved`).
         """,
         "hint": "for_each takes a map or a set of strings, and `var.crew` is a list: `for_each = toset(var.crew)`. Inside, use `each.key` (or `each.value`, the same for a set).",
         "solve": """cd $R/bunks
cat > main.tf <<'HCL'
resource "local_file" "bunk" {
  for_each = toset(var.crew)
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.value}"
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/bunks
cat > main.tf <<'HCL'
resource "local_file" "bunk" {
  for_each = var.crew
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.value}"
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/bunks
         [ "$(st . | sort | tr '\\n' ' ')" = 'local_file.bunk["Ada"] local_file.bunk["Bo"] local_file.bunk["Cyrus"] ' ] || exit 1
         [ "$(cat bunk-Bo.txt 2>/dev/null)" = "Bunk of Bo" ] || exit 1
         [ ! -f bunk-0.txt ] || exit 1
         noplan . || exit 1
         """},
        {"title": "Bo leaves",
         "background": """
         cd $R/bunks
         touch -d @1577836800 bunk-Ada.txt bunk-Cyrus.txt 2>/dev/null || true
         """,
         "text": """
         Now remove **Bo** from the crew list in `variables.tf` and apply.

         Read the plan before you say yes: only Bo's bunk may go. Ada's and Cyrus's bunks must **not** be rebuilt.
         """,
         "hint": "Edit the default to `[\"Ada\", \"Cyrus\"]`, then `terraform apply`. The plan should say `1 to destroy` and nothing else.",
         "solve": """cd $R/bunks
sed -i 's/"Ada", "Bo", "Cyrus"/"Ada", "Cyrus"/' variables.tf
terraform apply -auto-approve""",
         "wrong": "cd $R/bunks\nrm -f bunk-Bo.txt",
         "verify": """
         cd $R/bunks
         [ "$(st . | sort | tr '\\n' ' ')" = 'local_file.bunk["Ada"] local_file.bunk["Cyrus"] ' ] || exit 1
         [ ! -f bunk-Bo.txt ] || exit 1
         [ "$(stat -c %Y bunk-Ada.txt)" = "1577836800" ] && [ "$(stat -c %Y bunk-Cyrus.txt)" = "1577836800" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    count knows positions, so removing from the middle shifts every index after it. for_each knows **keys**:
    remove Bo and only `bunk["Bo"]` goes. A list goes in through `toset()`.
    """, "Terraform · Fleet roll call"),
    setup="""
    mkdir -p $R/bunks && cd $R/bunks
    """ + hcl("variables.tf", '''
    variable "crew" {
      type    = list(string)
      default = ["Ada", "Bo", "Cyrus"]
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "bunk" {
      count    = length(var.crew)
      filename = "${path.module}/bunk-${count.index}.txt"
      content  = "Bunk ${count.index}: ${var.crew[count.index]}"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 6.4 map + 6.5 · for expressions and splat --------------------------------------------------------------------------
tf_lab(
    "fleet-map",
    "🟡 Terraform # · Fleet roll call",
    "for_each over a map, then outputs built with for expressions (where splat can't help).",
    f"""
    # Fleet roll call

    In `/root/fleet`, `var.masts` is a map: ship name → number of masts. Nothing is built yet.

    Lessons: {L("6.4", "for_each")} · {L("6.5", "for and splat")}
    """,
    [
        {"title": "One file per ship",
         "text": """
         In `main.tf`, write **one** resource `local_file.mast` with `for_each` over `var.masts`:

         - file `<ship>.txt`, for example `osprey.txt`
         - content `<ship>: <masts> masts`, for example `osprey: 3 masts`

         Apply it. Adding a ship to the map later must need no new block.
         """,
         "hint": "With a map, `each.key` is the ship and `each.value` the number: `filename = \"${path.module}/${each.key}.txt\"`.",
         "solve": """cd $R/fleet
cat > main.tf <<'HCL'
resource "local_file" "mast" {
  for_each = var.masts
  filename = "${path.module}/${each.key}.txt"
  content  = "${each.key}: ${each.value} masts"
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/fleet
cat > main.tf <<'HCL'
resource "local_file" "kestrel" {
  filename = "${path.module}/kestrel.txt"
  content  = "kestrel: 2 masts"
}

resource "local_file" "osprey" {
  filename = "${path.module}/osprey.txt"
  content  = "osprey: 3 masts"
}

resource "local_file" "wren" {
  filename = "${path.module}/wren.txt"
  content  = "wren: 1 masts"
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/fleet
         [ "$(st . | sort | tr '\\n' ' ')" = 'local_file.mast["kestrel"] local_file.mast["osprey"] local_file.mast["wren"] ' ] || exit 1
         [ "$(cat osprey.txt 2>/dev/null)" = "osprey: 3 masts" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "The roll call",
         "text": """
         Add three outputs in `outputs.tf`, and apply:

         | output | value |
         |---|---|
         | `names` | every ship name in capitals: `["KESTREL", "OSPREY", "WREN"]` |
         | `files` | the `filename` of every `local_file.mast` |
         | `big_ships` | the ships with **more than one** mast: `["kestrel", "osprey"]` |

         ⛔ `local_file.mast` was made with for_each: think before you reach for `[*]`.
         """,
         "hint": "`[for name, m in var.masts : upper(name)]` · `[for f in local_file.mast : f.filename]` · `[for name, m in var.masts : name if m > 1]`. Splat only works on lists, sets and tuples; a for_each resource is a map.",
         "solve": """cd $R/fleet
cat > outputs.tf <<'HCL'
output "names" {
  value = [for name, m in var.masts : upper(name)]
}

output "files" {
  value = [for f in local_file.mast : f.filename]
}

output "big_ships" {
  value = [for name, m in var.masts : name if m > 1]
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/fleet
cat > outputs.tf <<'HCL'
output "names" {
  value = [for name, m in var.masts : upper(name)]
}

output "files" {
  value = local_file.mast[*].filename
}

output "big_ships" {
  value = [for name, m in var.masts : name if m > 1]
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/fleet
         terraform output -json 2>/dev/null | $PY -c "
import json,sys,os
o=json.load(sys.stdin)
ok=(o['names']['value']==['KESTREL','OSPREY','WREN'] and o['big_ships']['value']==['kestrel','osprey']
    and sorted(os.path.basename(f) for f in o['files']['value'])==['kestrel.txt','osprey.txt','wren.txt'])
sys.exit(0 if ok else 1)" || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    for_each over a map gives `each.key` and `each.value`. `[for ... : ...]` transforms and `if` filters. Splat
    `[*]` reads lists; a for_each resource is a map, so read it with a for expression (or `values(...)[*]`).
    """, "Terraform · Pack the crate"),
    setup="""
    mkdir -p $R/fleet && cd $R/fleet
    """ + hcl("variables.tf", '''
    variable "masts" {
      type = map(number)
      default = {
        kestrel = 2
        osprey  = 3
        wren    = 1
      }
    }
    ''') + """
    """ + hcl("versions.tf", '''
    terraform {
      required_providers {
        local = {
          source = "hashicorp/local"
        }
      }
    }
    ''') + """
    echo '# one local_file "mast" per ship goes here' > main.tf
    terraform init -input=false >/dev/null
    """,
)

# 6.6 · dynamic blocks -----------------------------------------------------------------------------------------------
tf_lab(
    "crate",
    "🟡 Terraform # · Pack the crate",
    "Replace repeated nested blocks with one dynamic block, then add an item without touching the code.",
    f"""
    # Pack the crate

    In `/root/crate`, the data source `archive_file` packs the ship's notes into `crate.zip`, one nested
    `source` block per note. Someone forgot `sail.txt`, and every new note means another block by hand.

    Lesson: {L("6.6", "dynamic blocks")}
    """,
    [
        {"title": "One stencil",
         "text": """
         Replace the literal `source` blocks with **one** `dynamic "source"` block over `var.notes`, so the crate holds
         **every** note (`hull.txt`, `mast.txt`, `sail.txt`). Apply and check: `unzip -l crate.zip`.
         """,
         "hint": "`dynamic \"source\" { for_each = var.notes  content { filename = source.key  content = source.value } }`. Inside, the item is named after the block label, not `each`.",
         "solve": """cd $R/crate
cat > main.tf <<'HCL'
data "archive_file" "crate" {
  type        = "zip"
  output_path = "${path.module}/crate.zip"

  dynamic "source" {
    for_each = var.notes
    content {
      filename = source.key
      content  = source.value
    }
  }
}

output "crate_size" {
  value = data.archive_file.crate.output_size
}
HCL
terraform apply -auto-approve
unzip -l crate.zip || true""",
         "wrong": """cd $R/crate
cat > main.tf <<'HCL'
data "archive_file" "crate" {
  type        = "zip"
  output_path = "${path.module}/crate.zip"

  source {
    filename = "hull.txt"
    content  = var.notes["hull.txt"]
  }
  source {
    filename = "mast.txt"
    content  = var.notes["mast.txt"]
  }
  source {
    filename = "sail.txt"
    content  = var.notes["sail.txt"]
  }
}

output "crate_size" {
  value = data.archive_file.crate.output_size
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/crate
         grep -q 'dynamic "source"' main.tf || exit 1
         ! grep -Eq '^[[:space:]]*source[[:space:]]*\\{' main.tf || exit 1
         $PY -c "import zipfile,sys; sys.exit(sorted(zipfile.ZipFile('crate.zip').namelist())!=['hull.txt','mast.txt','sail.txt'])" || exit 1
         noplan . || exit 1
         """},
        {"title": "A new note",
         "background": """
         cd $R/crate
         md5sum main.tf > /tmp/crate_md5
         """,
         "text": """
         The deck needs a note too: `deck.txt` saying `Teak, scrubbed daily`.

         Put it in the crate **without editing `main.tf`**: set `notes` in a `terraform.tfvars` file (keep the three
         other notes) and apply.
         """,
         "hint": "terraform.tfvars is loaded automatically. Write the whole map: `notes = { \"hull.txt\" = \"...\", ..., \"deck.txt\" = \"Teak, scrubbed daily\" }` (copy the three values from variables.tf).",
         "solve": """cd $R/crate
cat > terraform.tfvars <<'HCL'
notes = {
  "hull.txt" = "Oak, tarred twice"
  "mast.txt" = "Pine, 20 m"
  "sail.txt" = "Canvas, patched"
  "deck.txt" = "Teak, scrubbed daily"
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/crate
cat > terraform.tfvars <<'HCL'
notes = {
  "deck.txt" = "Teak, scrubbed daily"
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/crate
         md5sum -c /tmp/crate_md5 >/dev/null 2>&1 || exit 1
         $PY -c "
import zipfile,sys
z=zipfile.ZipFile('crate.zip')
ok=sorted(z.namelist())==['deck.txt','hull.txt','mast.txt','sail.txt'] and z.read('deck.txt')==b'Teak, scrubbed daily'
sys.exit(0 if ok else 1)" || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    `dynamic "LABEL"` repeats a nested block: `for_each` picks the items, `content` is one block, and the item is
    `LABEL.key` / `LABEL.value`. The list now lives in data, so a new note is a new value, not new code.
    """, "BOSS · The fleet yard"),
    setup="""
    mkdir -p $R/crate && cd $R/crate
    """ + hcl("variables.tf", '''
    variable "notes" {
      type = map(string)
      default = {
        "hull.txt" = "Oak, tarred twice"
        "mast.txt" = "Pine, 20 m"
        "sail.txt" = "Canvas, patched"
      }
    }
    ''') + hcl("main.tf", '''
    data "archive_file" "crate" {
      type        = "zip"
      output_path = "${path.module}/crate.zip"

      source {
        filename = "hull.txt"
        content  = var.notes["hull.txt"]
      }
      source {
        filename = "mast.txt"
        content  = var.notes["mast.txt"]
      }
    }

    output "crate_size" {
      value = data.archive_file.crate.output_size
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# boss (6.R) -------------------------------------------------------------------------------------------------------
tf_lab(
    "fleet-yard",
    "🔴 Terraform BOSS · The fleet yard",
    "Five dynamic-configuration faults in one fleet yard. Only the goal is given.",
    f"""
    # 🔴 BOSS · The fleet yard

    The fleet yard in `/root/yard` won't even plan. You only get the **goal**.

    Covers Module 6: {L("6.1", "conditionals")} · {L("6.2", "functions")} · {L("6.4", "for_each")} · {L("6.5", "for and splat")} · {L("6.6", "dynamic")}
    """,
    [
        {"title": "Open the yard",
         "text": """
         In `/root/yard`, reach this state:
         - `terraform validate` says Success and `terraform plan` says **No changes**
         - one bunk per crew member, **keyed by name** (`local_file.bunk["Ada"]`...), each file saying `Bunk of <name>`
         - `manifest.txt` says exactly `PROD-KESTREL: 3 masts, flag violet`
         - the same blueprint in dev (`-var env=dev`) would give `DEV-KESTREL`, **1** mast and flag **grey**
         - `crate.zip` holds every note in `var.notes`
         - `terraform output bunks` lists every bunk's filename

         ⛔ When someone leaves the crew later, only their bunk may be destroyed.
         """,
         "hint": "Go error by error: validate, then plan. Look for: a list given to for_each, a conditional whose two sides have different types, a function that doesn't exist, the wrong item name inside a dynamic block, and a splat on a for_each resource.",
         "solve": """cd $R/yard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('for_each = var.crew','for_each = toset(var.crew)')
t=t.replace('["violet"]','"violet"')
t=t.replace('shipname(var.env, var.ship)','upper("${var.env}-${var.ship}")')
t=t.replace('filename = each.key\\n      content  = each.value','filename = source.key\\n      content  = source.value')
open('main.tf','w').write(t)
o=open('outputs.tf').read().replace('local_file.bunk[*].filename','[for b in local_file.bunk : b.filename]')
open('outputs.tf','w').write(o)
PY
terraform validate
terraform apply -auto-approve""",
         "wrong": """cd $R/yard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('for_each = var.crew','count    = length(var.crew)')
t=t.replace('bunk-${each.key}.txt','bunk-${var.crew[count.index]}.txt').replace('Bunk of ${each.value}','Bunk of ${var.crew[count.index]}')
t=t.replace('["violet"]','"violet"')
t=t.replace('shipname(var.env, var.ship)','upper("${var.env}-${var.ship}")')
t=t.replace('filename = each.key\\n      content  = each.value','filename = source.key\\n      content  = source.value')
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/yard
         terraform validate >/dev/null 2>&1 || exit 1
         s=$(st . | sort | tr '\\n' ' ')
         [ "$s" = 'data.archive_file.crate local_file.bunk["Ada"] local_file.bunk["Bo"] local_file.bunk["Cyrus"] local_file.manifest ' ] || exit 1
         [ "$(cat bunk-Cyrus.txt 2>/dev/null)" = "Bunk of Cyrus" ] || exit 1
         [ "$(cat manifest.txt 2>/dev/null)" = "PROD-KESTREL: 3 masts, flag violet" ] || exit 1
         [ "$(echo 'local.label' | terraform console -var env=dev 2>/dev/null)" = '"DEV-KESTREL"' ] || exit 1
         [ "$(echo 'local.masts' | terraform console -var env=dev 2>/dev/null)" = "1" ] || exit 1
         [ "$(echo 'local.flag' | terraform console -var env=dev 2>/dev/null)" = '"grey"' ] || exit 1
         $PY -c "import zipfile,sys; sys.exit(sorted(zipfile.ZipFile('crate.zip').namelist())!=['hull.txt','mast.txt'])" || exit 1
         terraform output -json bunks 2>/dev/null | $PY -c "import json,sys,os; sys.exit(sorted(os.path.basename(f) for f in json.load(sys.stdin))!=['bunk-Ada.txt','bunk-Bo.txt','bunk-Cyrus.txt'])" || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    `toset()` for for_each, matching types in a conditional, built-in functions only, `source.value` inside
    `dynamic "source"`, and a for expression where splat can't reach: the whole of Module 6 in one yard. ⚒
    """),
    setup="""
    mkdir -p $R/yard && cd $R/yard
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "prod"
    }

    variable "ship" {
      type    = string
      default = "Kestrel"
    }

    variable "crew" {
      type    = list(string)
      default = ["Ada", "Bo", "Cyrus"]
    }

    variable "notes" {
      type = map(string)
      default = {
        "hull.txt" = "Oak"
        "mast.txt" = "Pine"
      }
    }
    ''') + hcl("main.tf", '''
    locals {
      masts = var.env == "prod" ? 3 : 1
      flag  = var.env == "prod" ? ["violet"] : "grey"
      label = shipname(var.env, var.ship)
    }

    resource "local_file" "bunk" {
      for_each = var.crew
      filename = "${path.module}/bunk-${each.key}.txt"
      content  = "Bunk of ${each.value}"
    }

    resource "local_file" "manifest" {
      filename = "${path.module}/manifest.txt"
      content  = "${local.label}: ${local.masts} masts, flag ${local.flag}"
    }

    data "archive_file" "crate" {
      type        = "zip"
      output_path = "${path.module}/crate.zip"

      dynamic "source" {
        for_each = var.notes
        content {
          filename = each.key
          content  = each.value
        }
      }
    }
    ''') + hcl("outputs.tf", '''
    output "bunks" {
      value = local_file.bunk[*].filename
    }

    output "crate_size" {
      value = data.archive_file.crate.output_size
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

labkit.structure(TF, ORDER)
with open(os.path.join(ROOT, "tools", "tf_spec.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(SPEC, f, indent=1)

LINKS = {"0.2": "first-apply", "0.3": "first-apply", "3.1": "first-apply", "2.1": "fix-the-blueprint",
         "2.2": "fix-the-blueprint", "3.3": "fix-the-blueprint", "2.3": "references", "3.5": "references",
         "2.4": "layout-and-fmt", "2.5": "layout-and-fmt", "3.4": "read-the-plan", "3.6": "half-built",
         "3.7": "remove-one", "4.2": "versions-lock", "4.3": "versions-lock", "4.5": "two-harbors",
         "3.R": "shipyard-in-trouble", "4.R": "shipyard-in-trouble",
         "3.2": "new-supplier", "4.1": "new-supplier", "4.4": "no-secrets", "4.6": "rules-on-the-door",
         "5.1": "harbor-register", "5.2": "harbor-register", "5.3": "fill-the-blanks", "5.4": "type-check",
         "5.5": "type-check", "5.6": "who-wins", "5.7": "delivery-receipt", "5.8": "margin-note",
         "5.R": "order-form",
         "6.1": "two-ships", "6.2": "two-ships", "6.3": "bunk-shift", "6.4": "bunk-shift", "6.5": "fleet-map",
         "6.6": "crate", "6.R": "fleet-yard"}
with open(os.path.join(ROOT, "labs-terraform.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"_comment": "Terraform lesson code -> Killercoda lab URL (lab_links.py --course terraform)",
               **{k: KC + v for k, v in LINKS.items()}}, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"wrote {len(ORDER)} Terraform labs in {TF}")
