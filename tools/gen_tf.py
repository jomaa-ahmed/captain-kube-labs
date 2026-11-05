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
         "fleet-yard",
         "hidden-orders", "shipyard-rules", "timber-change", "order-inspector", "lookout",
         "dock-rules",
         "ledger-reading", "harbor-vault", "pink-hull", "slipways",
         "the-vault",
         "the-index", "stray-ship", "new-names", "hand-over", "four-doors",
         "the-audit",
         "first-kit", "sealed-kit", "kit-sources", "fleet-kit",
         "kit-yard"]
BOSSES = {"shipyard-in-trouble", "order-form", "fleet-yard", "dock-rules", "the-vault", "the-audit", "kit-yard"}

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

# 7.1 · depends_on -----------------------------------------------------------------------------------------------
tf_lab(
    "hidden-orders",
    "🔧 Terraform # · Hidden orders",
    "A data source reads a file before it exists: add depends_on, then replace it with a plain reference.",
    f"""
    # Hidden orders

    In `/root/orders`, Terraform writes `orders.txt`, and a data source reads it to copy it into `crew.txt`.
    Nothing in the code tells Terraform the file must exist first, so the very first plan fails.

    Try it:
    ```
    cd /root/orders
    terraform plan
    ```

    Lesson: {L("7.1", "depends_on")}
    """,
    [
        {"title": "Wait for the orders",
         "text": """
         Tell Terraform that `data.local_file.orders` must wait for `local_file.orders`, then apply.

         `crew.txt` must say `build 3 masts`.
         """,
         "hint": "Inside the data block: `depends_on = [local_file.orders]`. A whole resource, not one of its attributes.",
         "solve": """cd $R/orders
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('data "local_file" "orders" {\\n  filename = "${path.module}/orders.txt"', 'data "local_file" "orders" {\\n  filename   = "${path.module}/orders.txt"\\n  depends_on = [local_file.orders]')
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "wrong": """cd $R/orders
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('data "local_file" "orders" {\\n  filename = "${path.module}/orders.txt"', 'data "local_file" "orders" {\\n  filename   = "${path.module}/orders.txt"\\n  depends_on = [local_file.orders.content]')
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/orders
         grep -q 'depends_on' main.tf || exit 1
         st . | grep -qx local_file.crew || exit 1
         [ "$(cat crew.txt 2>/dev/null)" = "build 3 masts" ] || exit 1
         """},
        {"title": "References first",
         "text": """
         It works, but HashiCorp calls `depends_on` a last resort. Here a plain reference says the same thing.

         Remove the data source and the `depends_on`, and let `local_file.crew` read **`local_file.orders.content`** directly.
         Apply: `crew.txt` is unchanged, and the plan ends with **No changes**.
         """,
         "hint": "A reference is an implicit dependency: `content = local_file.orders.content`. Then delete the whole `data \"local_file\" \"orders\"` block.",
         "solve": """cd $R/orders
cat > main.tf <<'HCL'
resource "local_file" "orders" {
  filename = "${path.module}/orders.txt"
  content  = "build 3 masts"
}

resource "local_file" "crew" {
  filename = "${path.module}/crew.txt"
  content  = local_file.orders.content
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/orders
sed -i '/depends_on/d' main.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/orders
         ! grep -q 'depends_on' main.tf || exit 1
         ! grep -q '^data ' main.tf || exit 1
         ! st . | grep -q '^data\\.' || exit 1
         [ "$(cat crew.txt 2>/dev/null)" = "build 3 masts" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A data source is read during plan, so it can't see a file that apply hasn't written yet: `depends_on` makes it
    wait. But a reference (`local_file.orders.content`) is an implicit dependency that does the same job, and it's
    clearer. References first, `depends_on` for what no reference can show.
    """, "Terraform · Shipyard rules"),
    setup="""
    mkdir -p $R/orders && cd $R/orders
    """ + hcl("main.tf", '''
    resource "local_file" "orders" {
      filename = "${path.module}/orders.txt"
      content  = "build 3 masts"
    }

    data "local_file" "orders" {
      filename = "${path.module}/orders.txt"
    }

    resource "local_file" "crew" {
      filename = "${path.module}/crew.txt"
      content  = data.local_file.orders.content
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# 7.2 + 7.3 · lifecycle -----------------------------------------------------------------------------------------------
tf_lab(
    "shipyard-rules",
    "🟡 Terraform # · Shipyard rules",
    "create_before_destroy for a replacement, prevent_destroy for the ledger, ignore_changes for the paint.",
    f"""
    # Shipyard rules

    `/root/rules` builds three things: a **dock** (replaced whenever `var.build` changes), the **ledger** and the
    **hull**. Each needs a different shipyard rule, in its `lifecycle` block.

    Lessons: {L("7.2", "create_before_destroy")} · {L("7.3", "prevent_destroy and ignore_changes")}
    """,
    [
        {"title": "New dock first",
         "text": """
         Make dock replacements **create the new dock first**, then destroy the old one.

         Then set the default of `build` to `"v2"` in `variables.tf` and apply. Check with
         `terraform plan -var build=v3`: it must show `+/- create replacement and then destroy`.
         """,
         "hint": "`lifecycle { create_before_destroy = true }` inside `terraform_data.dock`. Lifecycle values must be literals.",
         "solve": """cd $R/rules
sed -i 's|  triggers_replace = var.build|&\\n\\n  lifecycle {\\n    create_before_destroy = true\\n  }|' main.tf
sed -i 's/default = "v1"/default = "v2"/' variables.tf
terraform apply -auto-approve
terraform plan -var build=v3""",
         "wrong": """cd $R/rules
sed -i 's/default = "v1"/default = "v2"/' variables.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/rules
         [ "$(attr . terraform_data.dock triggers_replace)" = "v2" ] || exit 1
         terraform plan -var build=v3 -no-color -lock=false 2>&1 | grep -q '+/- create replacement and then destroy' || exit 1
         noplan . || exit 1
         """},
        {"title": "Never scrap the ledger",
         "text": """
         The ledger must survive any `terraform destroy`. Seal it so Terraform **refuses** to destroy it, and apply.

         Check: `terraform plan -destroy` must stop with `Instance cannot be destroyed`.
         """,
         "hint": "`lifecycle { prevent_destroy = true }` inside `local_file.ledger`.",
         "solve": """cd $R/rules
sed -i 's|  content  = "every ship we ever built"|&\\n\\n  lifecycle {\\n    prevent_destroy = true\\n  }|' main.tf
terraform apply -auto-approve
terraform plan -destroy || true""",
         "wrong": "cd $R/rules\nchmod 444 ledger.txt",
         "verify": """
         cd $R/rules
         [ -f ledger.txt ] || exit 1
         terraform plan -destroy -no-color -lock=false 2>&1 | grep -q 'Instance cannot be destroyed' || exit 1
         noplan . || exit 1
         """},
        {"title": "Leave the paint alone",
         "text": """
         The harbor repaints the hull whenever it likes and passes the colour in `var.paint`. Terraform must
         **stop updating** the hull's `input` after it's built, but keep using `var.paint` when it creates the hull.

         Check: `terraform plan -var paint=red` must say **No changes**.
         """,
         "hint": "`lifecycle { ignore_changes = [input] }` inside `terraform_data.hull`. Keep `paint = var.paint` in the input.",
         "solve": """cd $R/rules
sed -i 's|  input = { paint = var.paint, masts = 3 }|&\\n\\n  lifecycle {\\n    ignore_changes = [input]\\n  }|' main.tf
terraform plan -var paint=red""",
         "wrong": """cd $R/rules
sed -i 's|paint = var.paint|paint = "blue"|' main.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/rules
         grep -q 'paint = var.paint' main.tf || exit 1
         terraform plan -var paint=red -input=false -detailed-exitcode -lock=false >/dev/null 2>&1 || exit 1
         terraform show -json | $PY -c "
import json,sys
d=json.load(sys.stdin)
r=[x for x in d['values']['root_module']['resources'] if x['address']=='terraform_data.hull'][0]
sys.exit(0 if r['values']['input']['paint']=='blue' else 1)" || exit 1
         """},
    ],
    done("""
    Three rules, three lifecycle arguments: `create_before_destroy` flips the replacement order (`+/-`),
    `prevent_destroy` refuses destroys and replacements (until someone deletes the block), and `ignore_changes`
    uses a value on create but never updates it.
    """, "Terraform · Timber change"),
    setup="""
    mkdir -p $R/rules && cd $R/rules
    """ + hcl("variables.tf", '''
    variable "build" {
      type    = string
      default = "v1"
    }

    variable "paint" {
      type    = string
      default = "blue"
    }
    ''') + hcl("main.tf", '''
    resource "terraform_data" "dock" {
      triggers_replace = var.build
    }

    resource "local_file" "ledger" {
      filename = "${path.module}/ledger.txt"
      content  = "every ship we ever built"
    }

    resource "terraform_data" "hull" {
      input = { paint = var.paint, masts = 3 }
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 7.4 · replace_triggered_by + -replace --------------------------------------------------------------------------------
tf_lab(
    "timber-change",
    "🟡 Terraform # · Timber change",
    "Rebuild the hull when the recipe changes, then rebuild it once with -replace.",
    f"""
    # Timber change

    In `/root/timber`, the hull doesn't mention the recipe, so when `var.recipe` changes from oak to pine,
    Terraform does nothing. The shipwright's rule: new timber, new hull.

    Lesson: {L("7.4", "replace_triggered_by")}
    """,
    [
        {"title": "New timber, new hull",
         "text": """
         Make `local_file.hull` be **replaced** whenever `var.recipe` changes. Don't put the recipe in the hull's content.

         Check: `terraform plan -var recipe=pine` must say
         `local_file.hull will be replaced due to changes in replace_triggered_by`. Apply with the default (oak) at the end.
         """,
         "hint": "replace_triggered_by only takes resources. Hold the value in one: `resource \"terraform_data\" \"recipe\" { input = var.recipe }`, then `replace_triggered_by = [terraform_data.recipe]` in the hull's lifecycle.",
         "solve": """cd $R/timber
cat > main.tf <<'HCL'
resource "terraform_data" "recipe" {
  input = var.recipe
}

resource "local_file" "hull" {
  filename = "${path.module}/hull.txt"
  content  = "hull"

  lifecycle {
    replace_triggered_by = [terraform_data.recipe]
  }
}
HCL
terraform apply -auto-approve
terraform plan -var recipe=pine""",
         "wrong": """cd $R/timber
cat > main.tf <<'HCL'
resource "local_file" "hull" {
  filename = "${path.module}/hull.txt"
  content  = "hull"

  lifecycle {
    replace_triggered_by = [var.recipe]
  }
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/timber
         ! grep -q 'content.*recipe' main.tf || exit 1
         terraform plan -var recipe=pine -no-color -lock=false 2>&1 | grep -q 'local_file.hull will be replaced due to changes in replace_triggered_by' || exit 1
         noplan . || exit 1
         """},
        {"title": "Rebuild it once",
         "background": """
         cd $R/timber
         touch -d @1577836800 hull.txt 2>/dev/null || true
         md5sum *.tf > /tmp/timber_md5
         """,
         "text": """
         A crack in the hull: rebuild it **now**, once, without changing any code and without touching the recipe.
         Look at the plan first.
         """,
         "hint": "`terraform apply -replace=local_file.hull`. (`terraform taint` is deprecated, and it only marks the resource: nothing is rebuilt until the next apply.)",
         "solve": "cd $R/timber\nterraform apply -replace=local_file.hull -auto-approve",
         "wrong": "cd $R/timber\nterraform taint local_file.hull",
         "verify": """
         cd $R/timber
         md5sum -c /tmp/timber_md5 >/dev/null 2>&1 || exit 1
         [ -f hull.txt ] || exit 1
         [ "$(stat -c %Y hull.txt)" != "1577836800" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    `replace_triggered_by` takes resources (or their attributes), so a variable goes through `terraform_data`.
    For a one-time rebuild there's `-replace=ADDRESS`, and you see the plan before anything happens.
    """, "Terraform · The order inspector"),
    setup="""
    mkdir -p $R/timber && cd $R/timber
    """ + hcl("variables.tf", '''
    variable "recipe" {
      type    = string
      default = "oak"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "hull"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 7.5 + 7.6 · validation and conditions ---------------------------------------------------------------------------------
tf_lab(
    "order-inspector",
    "🟡 Terraform # · The order inspector",
    "Variable validation for bad input, then a precondition for a bad combination.",
    f"""
    # The order inspector

    In `/root/inspect`, anyone can order a ship for `env = "staging"` with nine masts, and Terraform happily plans it.
    Time for an inspector.

    Lessons: {L("7.5", "Variable validation")} · {L("7.6", "Preconditions and postconditions")}
    """,
    [
        {"title": "At the order desk",
         "text": """
         Add validation rules in `variables.tf`:
         - `env` accepts only `dev` or `prod`
         - `masts` accepts only 1 to 5

         Each with a clear `error_message`. A bad value must stop `terraform plan` with `Invalid value for variable`;
         `terraform plan -var env=prod -var masts=3` must still work.
         """,
         "hint": "`validation { condition = contains([\"dev\", \"prod\"], var.env)  error_message = \"...\" }`. The condition is true for a GOOD value. For masts: `var.masts >= 1 && var.masts <= 5`.",
         "solve": """cd $R/inspect
cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.env)
    error_message = "env must be dev or prod."
  }
}

variable "masts" {
  type    = number
  default = 2

  validation {
    condition     = var.masts >= 1 && var.masts <= 5
    error_message = "A ship has 1 to 5 masts."
  }
}

variable "crew" {
  type    = list(string)
  default = ["Ada", "Bo"]
}
HCL
terraform plan -var env=staging || true""",
         "wrong": """cd $R/inspect
cat > variables.tf <<'HCL'
variable "env" {
  type    = string
  default = "dev"

  validation {
    condition     = var.env != "staging"
    error_message = "No staging."
  }
}

variable "masts" {
  type    = number
  default = 2

  validation {
    condition     = var.masts <= 5
    error_message = "Too many masts."
  }
}

variable "crew" {
  type    = list(string)
  default = ["Ada", "Bo"]
}
HCL""",
         "verify": """
         cd $R/inspect
         bad() { terraform plan -input=false -lock=false -no-color "$@" 2>&1 | grep -q 'Invalid value for variable'; }
         bad -var env=staging || exit 1
         bad -var env=test || exit 1
         bad -var masts=9 || exit 1
         bad -var masts=0 || exit 1
         terraform plan -input=false -lock=false -var env=prod -var masts=2 >/dev/null 2>&1 || exit 1
         """},
        {"title": "Before the build",
         "text": """
         Each mast needs at least one crew member. Add a **precondition** to `local_file.ship` so that a plan with more
         masts than crew stops with `Resource precondition failed`.

         With the default crew (Ada, Bo): `-var masts=2` plans fine, `-var masts=3` must fail.
         """,
         "hint": "Inside the resource: `lifecycle { precondition { condition = length(var.crew) >= var.masts  error_message = \"...\" } }`.",
         "solve": """cd $R/inspect
sed -i 's|  content  = "${var.env}: ${var.masts} masts, ${length(var.crew)} crew"|&\\n\\n  lifecycle {\\n    precondition {\\n      condition     = length(var.crew) >= var.masts\\n      error_message = "Each mast needs at least one crew member."\\n    }\\n  }|' main.tf
terraform plan -var masts=3 || true""",
         "wrong": """cd $R/inspect
$PY - <<'PY'
t=open('variables.tf').read()
t=t.replace('error_message = "A ship has 1 to 5 masts."','error_message = "A ship has 1 to 5 masts."\\n  }\\n\\n  validation {\\n    condition     = var.masts <= length(var.crew)\\n    error_message = "Not enough crew."',1)
open('variables.tf','w').write(t)
PY""",
         "verify": """
         cd $R/inspect
         terraform plan -input=false -lock=false -no-color -var masts=3 2>&1 | grep -q 'Resource precondition failed' || exit 1
         terraform plan -input=false -lock=false -var masts=2 >/dev/null 2>&1 || exit 1
         """},
    ],
    done("""
    Validation checks one input, at the door, with a condition that's true for good values. A precondition checks
    an assumption about a resource or a combination of values (crew vs masts). Both stop the plan.
    """, "Terraform · The lookout"),
    setup="""
    mkdir -p $R/inspect && cd $R/inspect
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "dev"
    }

    variable "masts" {
      type    = number
      default = 2
    }

    variable "crew" {
      type    = list(string)
      default = ["Ada", "Bo"]
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "ship" {
      filename = "${path.module}/ship.txt"
      content  = "${var.env}: ${var.masts} masts, ${length(var.crew)} crew"
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# 7.7 + 7.8 · check blocks and provisioners -----------------------------------------------------------------------------
tf_lab(
    "lookout",
    "🔧 Terraform # · The lookout",
    "A check block that warns without stopping, then a tainted resource from a failed provisioner.",
    f"""
    # The lookout

    In `/root/lookout`, the ship's log is written from `var.weather`. And something went wrong at launch.

    Lessons: {L("7.7", "check blocks")} · {L("7.8", "Provisioners")}
    """,
    [
        {"title": "Storm warning",
         "text": """
         Add a `check` block named `calm_seas` that **warns** when the log mentions `storm`, but never stops the run.

         - `terraform plan -var 'weather=storm ahead'` must succeed **and** show `Check block assertion failed`
         - `terraform plan` (calm weather) must show no warning
         """,
         "hint": "`check \"calm_seas\" { assert { condition = !strcontains(local_file.log.content, \"storm\")  error_message = \"...\" } }`, at the top level, not inside the resource.",
         "solve": """cd $R/lookout
cat >> main.tf <<'HCL'

check "calm_seas" {
  assert {
    condition     = !strcontains(local_file.log.content, "storm")
    error_message = "The log mentions a storm."
  }
}
HCL
terraform plan -var 'weather=storm ahead'""",
         "wrong": """cd $R/lookout
sed -i 's|  content  = var.weather|&\\n\\n  lifecycle {\\n    precondition {\\n      condition     = !strcontains(var.weather, "storm")\\n      error_message = "Storm."\\n    }\\n  }|' main.tf""",
         "verify": """
         cd $R/lookout
         grep -q 'check "calm_seas"' main.tf || exit 1
         out=$(terraform plan -input=false -lock=false -no-color -var 'weather=storm ahead' 2>&1) || exit 1
         echo "$out" | grep -q 'Check block assertion failed' || exit 1
         ! terraform plan -input=false -lock=false -no-color 2>&1 | grep -q 'Check block assertion failed' || exit 1
         """},
        {"title": "A failed launch",
         "background": """
         cd $R/lookout
         cat > launch.tf <<'HCL'
         resource "terraform_data" "launch" {
           provisioner "local-exec" {
             command = "exit 1"
           }
         }
         HCL
         sed -i 's/^         //' launch.tf
         terraform apply -auto-approve -input=false >/dev/null 2>&1 || true
         """,
         "text": """
         Someone added `launch.tf`: a `terraform_data.launch` with a `local-exec` provisioner. The apply failed.

         Run `terraform plan` and read what Terraform now thinks of `terraform_data.launch`. Then fix the
         command (make it `echo launched`) and apply, so the plan ends with **No changes**.

         ⛔ `terraform untaint` alone hides the problem: the command would still fail next time.
         """,
         "hint": "A failed creation-time provisioner marks the resource **tainted**, so the next apply replaces it. Fix the command in launch.tf, then `terraform apply`.",
         "solve": "cd $R/lookout\nsed -i 's/command = \"exit 1\"/command = \"echo launched\"/' launch.tf\nterraform apply -auto-approve",
         "wrong": "cd $R/lookout\nterraform untaint terraform_data.launch",
         "verify": """
         cd $R/lookout
         ! grep -q 'exit 1' launch.tf || exit 1
         st . | grep -qx terraform_data.launch || exit 1
         terraform show -json | $PY -c "
import json,sys
d=json.load(sys.stdin)
r=[x for x in d['values']['root_module']['resources'] if x['address']=='terraform_data.launch']
sys.exit(0 if r and not r[0].get('tainted') else 1)" || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A `check` block only warns: the run goes on, so it's for watching, not blocking. A failed creation-time
    provisioner taints the resource: Terraform replaces it on the next apply. And provisioners stay the last resort.
    """, "BOSS · Dock rules"),
    setup="""
    mkdir -p $R/lookout && cd $R/lookout
    """ + hcl("variables.tf", '''
    variable "weather" {
      type    = string
      default = "calm seas"
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "log" {
      filename = "${path.module}/log.txt"
      content  = var.weather
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# boss (7.R) -------------------------------------------------------------------------------------------------------
tf_lab(
    "dock-rules",
    "🔴 Terraform BOSS · Dock rules",
    "Five dependency and lifecycle faults in one dock. Only the goal is given.",
    f"""
    # 🔴 BOSS · Dock rules

    The dock in `/root/dock` won't even initialise, and one rule nobody wrote down is missing. You only get the **goal**.

    Covers Module 7: {L("7.1", "depends_on")} · {L("7.2", "create_before_destroy")} · {L("7.3", "prevent_destroy")} · {L("7.4", "replace_triggered_by")} · {L("7.5", "validation")}
    """,
    [
        {"title": "Open the dock",
         "text": """
         In `/root/dock`, reach this state:
         - `terraform init` and `terraform validate` succeed, apply works, and `terraform plan` says **No changes**
         - `crew.txt` holds the same text as `orders.txt` (the data source stays)
         - `env` only accepts `dev` or `prod`: `-var env=staging` stops the plan
         - the hull is **replaced** whenever `var.recipe` changes
         - a dock replacement (`-var build=v9`) **creates the new dock first**
         - `terraform plan -destroy` stops with `Instance cannot be destroyed` (the ledger)
         """,
         "hint": "Go error by error: init, validate, then plan. Look for: depends_on on an attribute, a variable in replace_triggered_by, a variable in lifecycle, a validation condition written backwards, and a seal nobody added.",
         "solve": """cd $R/dock
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('depends_on = [local_file.orders.content]','depends_on = [local_file.orders]')
t=t.replace('replace_triggered_by = [var.recipe]','replace_triggered_by = [terraform_data.recipe]')
t=t.replace('create_before_destroy = var.safe','create_before_destroy = true')
t=t.replace('content  = "every ship we ever built"','content  = "every ship we ever built"\\n\\n  lifecycle {\\n    prevent_destroy = true\\n  }')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('!contains(["dev", "prod"], var.env)','contains(["dev", "prod"], var.env)')
open('variables.tf','w').write(v)
PY
terraform init
terraform validate
terraform apply -auto-approve""",
         "wrong": """cd $R/dock
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('depends_on = [local_file.orders.content]','depends_on = [local_file.orders]')
t=t.replace('replace_triggered_by = [var.recipe]','replace_triggered_by = [terraform_data.recipe]')
t=t.replace('create_before_destroy = var.safe','create_before_destroy = true')
open('main.tf','w').write(t)
v=open('variables.tf').read().replace('!contains(["dev", "prod"], var.env)','contains(["dev", "prod"], var.env)')
open('variables.tf','w').write(v)
PY
terraform init
terraform apply -auto-approve""",
         "verify": """
         cd $R/dock
         terraform validate >/dev/null 2>&1 || exit 1
         st . | grep -qx data.local_file.orders || exit 1
         [ "$(cat crew.txt 2>/dev/null)" = "$(cat orders.txt 2>/dev/null)" ] && [ -s crew.txt ] || exit 1
         p() { terraform plan -input=false -lock=false -no-color "$@" 2>&1; }
         p -var env=staging | grep -q 'Invalid value for variable' || exit 1
         p -var recipe=pine | grep -q 'local_file.hull will be replaced due to changes in replace_triggered_by' || exit 1
         p -var build=v9 | grep -q '+/- create replacement and then destroy' || exit 1
         p -destroy | grep -q 'Instance cannot be destroyed' || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A whole resource in `depends_on`, a `terraform_data` behind `replace_triggered_by`, literals in `lifecycle`, a
    validation condition that's true for good values, and a `prevent_destroy` seal: the whole of Module 7 in one dock. ⚒
    """),
    setup="""
    mkdir -p $R/dock && cd $R/dock
    """ + hcl("variables.tf", '''
    variable "env" {
      type    = string
      default = "prod"

      validation {
        condition     = !contains(["dev", "prod"], var.env)
        error_message = "env must be dev or prod."
      }
    }

    variable "recipe" {
      type    = string
      default = "oak"
    }

    variable "build" {
      type    = string
      default = "v1"
    }

    variable "safe" {
      type    = bool
      default = true
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "orders" {
      filename = "${path.module}/orders.txt"
      content  = "${var.env}: build 3 masts"
    }

    data "local_file" "orders" {
      filename   = "${path.module}/orders.txt"
      depends_on = [local_file.orders.content]
    }

    resource "local_file" "crew" {
      filename = "${path.module}/crew.txt"
      content  = data.local_file.orders.content
    }

    resource "terraform_data" "recipe" {
      input = var.recipe
    }

    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "hull"

      lifecycle {
        replace_triggered_by = [var.recipe]
      }
    }

    resource "terraform_data" "dock" {
      triggers_replace = var.build

      lifecycle {
        create_before_destroy = var.safe
      }
    }

    resource "local_file" "ledger" {
      filename = "${path.module}/ledger.txt"
      content  = "every ship we ever built"
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# 8.1 + 8.2 · reading the ledger -------------------------------------------------------------------------------------
tf_lab(
    "ledger-reading",
    "🟢 Terraform # · Reading the ledger",
    "Read a real object's ID from the state, then keep every state file out of Git.",
    f"""
    # Reading the ledger

    In `/root/ledger`, Terraform already built a hull and a ship with a random name. The state knows which
    real ship is ours. And the folder is a Git repository.

    Lessons: {L("8.1", "Why state exists")} · {L("8.2", "The local backend")}
    """,
    [
        {"title": "Which ship is ours?",
         "text": """
         Find the real name (the `id`) of `random_pet.ship` and write it, alone, into `/root/ledger/answer.txt`.

         ⛔ Read it the Terraform way, not by opening `terraform.tfstate` in an editor.
         """,
         "hint": "`terraform state show random_pet.ship` prints its attributes. Copy the `id` value (without quotes): `echo some-name > answer.txt`.",
         "solve": """cd $R/ledger
terraform state show -no-color random_pet.ship
terraform show -json | $PY -c "import json,sys; print([r['values']['id'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > answer.txt""",
         "wrong": "cd $R/ledger\necho guided-honeybee > answer.txt",
         "verify": """
         cd $R/ledger
         [ "$(tr -d ' \\n\\r"' < answer.txt 2>/dev/null)" = "$(attr . random_pet.ship id)" ] || exit 1
         """},
        {"title": "Never in Git",
         "text": """
         The state holds every attribute in plain text, and a second apply also writes `terraform.tfstate.backup`.
         Create a `.gitignore` so that Git ignores **every** state file and the `.terraform/` folder, but still tracks `main.tf`.

         Check with `git status`.
         """,
         "hint": "One pattern covers the state and its backup: `*.tfstate*`. Add `.terraform/` on a second line.",
         "solve": "cd $R/ledger\nprintf '*.tfstate*\\n.terraform/\\n' > .gitignore\ngit status --short",
         "wrong": "cd $R/ledger\necho 'terraform.tfstate' > .gitignore",
         "verify": """
         cd $R/ledger
         git check-ignore -q terraform.tfstate || exit 1
         git check-ignore -q terraform.tfstate.backup || exit 1
         git check-ignore -q .terraform/x || exit 1
         ! git check-ignore -q main.tf || exit 1
         """},
    ],
    done("""
    The state maps every address to a real object: `terraform state show` reads it safely. It holds secrets in
    plain text, and the local backend writes a `.backup` too, so `*.tfstate*` stays out of Git.
    """, "Terraform · Into the vault"),
    setup="""
    mkdir -p $R/ledger && cd $R/ledger
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "random_pet" "ship" {}
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    git init -q . 2>/dev/null || true
    """,
)

# 8.4 + 8.5 · migrating state ------------------------------------------------------------------------------------------
tf_lab(
    "harbor-vault",
    "🟡 Terraform # · Into the vault",
    "Migrate local state into a new backend without rebuilding anything, then move the path into a backend config file.",
    f"""
    # Into the vault

    In `/root/harbor`, the state is a plain `terraform.tfstate` next to the code. It's time to move the ledger
    into the vault: `vault/terraform.tfstate`. (On a real team that's an S3 bucket; the steps are the same.)

    Lessons: {L("8.4", "Remote state")} · {L("8.5", "Migrating state")}
    """,
    [
        {"title": "Move the ledger",
         "text": """
         Add this backend to the configuration and **migrate** the existing state into it:

         ```
         terraform {
           backend "local" {
             path = "vault/terraform.tfstate"
           }
         }
         ```

         Nothing may be rebuilt: `random_pet.ship` must keep its name. When the vault holds the state, delete the
         old `terraform.tfstate` (and its backup) from the folder. The plan must end with **No changes**.
         """,
         "hint": "`terraform init -migrate-state` copies the state (answer `yes`, or add `-force-copy`). `-reconfigure` would start the new backend empty.",
         "solve": """cd $R/harbor
cat > backend.tf <<'HCL'
terraform {
  backend "local" {
    path = "vault/terraform.tfstate"
  }
}
HCL
terraform init -migrate-state -force-copy -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform state list""",
         "wrong": """cd $R/harbor
cat > backend.tf <<'HCL'
terraform {
  backend "local" {
    path = "vault/terraform.tfstate"
  }
}
HCL
terraform init -reconfigure -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform apply -auto-approve""",
         "verify": """
         cd $R/harbor
         [ -f vault/terraform.tfstate ] && [ ! -f terraform.tfstate ] || exit 1
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/harbor_pet)" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "The path out of the code",
         "text": """
         Dev and prod will use different vaults, and a backend block can't use variables. Use **partial configuration**:

         - the `backend "local"` block stays, but **without** `path`
         - the path goes in a file `vault.tfbackend`: `path = "vault/terraform.tfstate"`
         - run `terraform init` with that file. Same state, nothing rebuilt, plan: **No changes**
         """,
         "hint": "`backend \"local\" {}` in backend.tf, then `terraform init -reconfigure -backend-config=vault.tfbackend`. The state stays where it is because the path is the same.",
         "solve": """cd $R/harbor
printf 'terraform {\\n  backend "local" {}\\n}\\n' > backend.tf
echo 'path = "vault/terraform.tfstate"' > vault.tfbackend
terraform init -reconfigure -backend-config=vault.tfbackend -input=false
terraform plan""",
         "wrong": """cd $R/harbor
printf 'terraform {\\n  backend "local" {}\\n}\\n' > backend.tf
terraform init -reconfigure -input=false""",
         "verify": """
         cd $R/harbor
         ! grep -q 'path' backend.tf || exit 1
         grep -q 'vault/terraform.tfstate' vault.tfbackend || exit 1
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/harbor_pet)" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Any backend change needs `terraform init`. `-migrate-state` copies the state, `-reconfigure` starts fresh, and the
    old local file stays behind until you delete it. Backend blocks take no variables: values go in with `-backend-config`.
    """, "Terraform · The pink hull"),
    setup="""
    mkdir -p $R/harbor && cd $R/harbor
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "random_pet" "ship" {}
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    terraform show -json | $PY -c "import json,sys; print([r['values']['id'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/harbor_pet
    """,
)

# 8.6 + 8.7 · drift and refresh-only ------------------------------------------------------------------------------------
tf_lab(
    "pink-hull",
    "🔧 Terraform # · The pink hull",
    "Fix drift the Terraform way, then accept a deliberate change with -refresh-only.",
    f"""
    # The pink hull

    In `/root/pink`, Terraform built a hull and a mast. Then people started changing things by hand.

    Lessons: {L("8.6", "Drift")} · {L("8.7", "Refresh-only mode")}
    """,
    [
        {"title": "Someone repainted it",
         "background": """
         cd $R/pink
         echo "painted pink" > hull.txt
         """,
         "text": """
         Someone wrote `painted pink` into `hull.txt` by hand. The blueprint is right: put the hull back
         **the Terraform way**. Read the plan first: what does Terraform want to do, and why?
         """,
         "hint": "`terraform plan` shows the drift (the local provider treats the changed file as gone), `terraform apply` rebuilds it from the code. Not `-refresh-only`: that would accept the pink hull.",
         "solve": "cd $R/pink\nterraform plan\nterraform apply -auto-approve",
         "wrong": "cd $R/pink\nterraform apply -refresh-only -auto-approve",
         "verify": """
         cd $R/pink
         [ "$(cat hull.txt)" = "oak, 3 masts" ] || exit 1
         st . | grep -qx local_file.hull || exit 1
         noplan . || exit 1
         """},
        {"title": "Scrapped on purpose",
         "background": """
         cd $R/pink
         rm -f mast.txt
         """,
         "text": """
         This time the change was **right**: the captain scrapped the mast on purpose, and `mast.txt` is gone.

         Record that in the state **without rebuilding the mast**, then update the code so it agrees.
         The plan must end with **No changes**, and `mast.txt` must not come back.
         """,
         "hint": "`terraform plan -refresh-only` shows the change, `terraform apply -refresh-only` records it in the state only. Then delete the `local_file.mast` block from main.tf.",
         "solve": """cd $R/pink
terraform plan -refresh-only
terraform apply -refresh-only -auto-approve
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'\\nresource "local_file" "mast" \\{.*?\\n\\}\\n?', '\\n', t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform plan""",
         "wrong": "cd $R/pink\nterraform apply -auto-approve",
         "verify": """
         cd $R/pink
         [ ! -f mast.txt ] || exit 1
         ! st . | grep -q 'local_file.mast' || exit 1
         ! grep -q '"mast"' main.tf || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Every plan refreshes first and shows drift; a normal apply puts the code back. When the real world is right,
    `-refresh-only` updates the state without touching anything real, and then the code has to follow.
    """, "Terraform · Parallel slipways"),
    setup="""
    mkdir -p $R/pink && cd $R/pink
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "local_file" "mast" {
      filename = "${path.module}/mast.txt"
      content  = "pine, 20 m"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 8.9 · workspaces -------------------------------------------------------------------------------------------------------
tf_lab(
    "slipways",
    "🟡 Terraform # · Parallel slipways",
    "One configuration, a state per workspace, then remove a workspace and everything in it.",
    f"""
    # Parallel slipways

    In `/root/slipways`, one blueprint builds a dock file. The shipyard wants a **dev** and a **prod** slipway,
    each with its own ledger.

    Lesson: {L("8.9", "CLI workspaces")}
    """,
    [
        {"title": "Two slipways",
         "text": """
         Change `main.tf` so the file is called `dock-<workspace>.txt` and says `masts: 3` in **prod**, `masts: 1` everywhere else.

         Then create the workspaces `dev` and `prod` and apply in **each** of them.
         """,
         "hint": "`terraform.workspace` holds the current name: `filename = \"${path.module}/dock-${terraform.workspace}.txt\"`, `content = \"masts: ${terraform.workspace == \"prod\" ? 3 : 1}\"`. Then `terraform workspace new dev`, apply, `terraform workspace new prod`, apply.",
         "solve": """cd $R/slipways
cat > main.tf <<'HCL'
resource "local_file" "dock" {
  filename = "${path.module}/dock-${terraform.workspace}.txt"
  content  = "masts: ${terraform.workspace == "prod" ? 3 : 1}"
}
HCL
terraform workspace new dev
terraform apply -auto-approve
terraform workspace new prod
terraform apply -auto-approve""",
         "wrong": """cd $R/slipways
cat > main.tf <<'HCL'
resource "local_file" "dock" {
  filename = "${path.module}/dock-${terraform.workspace}.txt"
  content  = "masts: ${terraform.workspace == "prod" ? 3 : 1}"
}
HCL
terraform workspace new dev
terraform apply -auto-approve""",
         "verify": """
         cd $R/slipways
         [ "$(cat dock-dev.txt 2>/dev/null)" = "masts: 1" ] || exit 1
         [ "$(cat dock-prod.txt 2>/dev/null)" = "masts: 3" ] || exit 1
         grep -q '"dock"' terraform.tfstate.d/dev/terraform.tfstate 2>/dev/null || exit 1
         grep -q '"dock"' terraform.tfstate.d/prod/terraform.tfstate 2>/dev/null || exit 1
         """},
        {"title": "Close a slipway",
         "background": """
         cd $R/slipways
         terraform workspace new test >/dev/null 2>&1 || terraform workspace select test >/dev/null 2>&1
         terraform apply -auto-approve -input=false >/dev/null 2>&1
         terraform workspace select default >/dev/null 2>&1
         """,
         "text": """
         Someone opened a `test` workspace and built `dock-test.txt` in it. Close that slipway **completely**:
         the workspace must disappear, and so must everything it built.
         """,
         "hint": "`terraform workspace delete test` refuses while the workspace still tracks resources. Select it, `terraform destroy`, go back to another workspace, then delete it.",
         "solve": """cd $R/slipways
terraform workspace select test
terraform destroy -auto-approve
terraform workspace select default
terraform workspace delete test""",
         "wrong": "cd $R/slipways\nterraform workspace delete -force test",
         "verify": """
         cd $R/slipways
         ! terraform workspace list 2>/dev/null | grep -qw test || exit 1
         [ ! -f dock-test.txt ] || exit 1
         [ -f dock-dev.txt ] && [ -f dock-prod.txt ] || exit 1
         """},
    ],
    done("""
    Each workspace keeps its own state (`terraform.tfstate.d/<name>/`), and `terraform.workspace` names it in the code.
    A workspace with resources can't be deleted: destroy first. And for separate credentials, use separate configurations.
    """, "BOSS · The vault"),
    setup="""
    mkdir -p $R/slipways && cd $R/slipways
    """ + hcl("main.tf", '''
    resource "local_file" "dock" {
      filename = "${path.module}/dock.txt"
      content  = "masts: 1"
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# boss (8.R) -------------------------------------------------------------------------------------------------------------
tf_lab(
    "the-vault",
    "🔴 Terraform BOSS · The vault",
    "A backend that won't initialise, state in the wrong place, drift and an open Git door. Only the goal is given.",
    f"""
    # 🔴 BOSS · The vault

    The yard in `/root/yard8` was built with local state. Someone started moving it to the vault, and stopped halfway.
    You only get the **goal**.

    Covers Module 8: {L("8.2", "local backend")} · {L("8.4", "remote state")} · {L("8.5", "migrating")} · {L("8.6", "drift")}
    """,
    [
        {"title": "Lock it in the vault",
         "text": """
         In `/root/yard8`, reach this state:
         - `terraform init` succeeds, and the state lives in **`vault/terraform.tfstate`**
         - no `terraform.tfstate` (or backup) is left in `/root/yard8`
         - `random_pet.ship` keeps its **current name**: nothing is rebuilt that doesn't need to be
         - `hull.txt` says what the blueprint says
         - `terraform plan` says **No changes**
         - Git ignores every state file (the folder is a repository)
         """,
         "hint": "Backend blocks can't use variables. Migrate (don't reconfigure) to keep the ship. Drift is fixed by a normal apply. One .gitignore pattern covers all state files.",
         "solve": """cd $R/yard8
sed -i 's|path = var.vault_path|path = "vault/terraform.tfstate"|' backend.tf
terraform init -migrate-state -force-copy -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform apply -auto-approve
printf '*.tfstate*\\n.terraform/\\n' > .gitignore""",
         "wrong": """cd $R/yard8
sed -i 's|path = var.vault_path|path = "vault/terraform.tfstate"|' backend.tf
terraform init -reconfigure -input=false
rm -f terraform.tfstate terraform.tfstate.backup
terraform apply -auto-approve
printf '*.tfstate*\\n.terraform/\\n' > .gitignore""",
         "verify": """
         cd $R/yard8
         [ -f vault/terraform.tfstate ] && [ ! -f terraform.tfstate ] && [ ! -f terraform.tfstate.backup ] || exit 1
         [ "$(attr . random_pet.ship id)" = "$(cat /tmp/yard8_pet)" ] || exit 1
         [ "$(cat hull.txt)" = "oak, 3 masts" ] || exit 1
         noplan . || exit 1
         git check-ignore -q terraform.tfstate && git check-ignore -q vault/terraform.tfstate && git check-ignore -q terraform.tfstate.backup || exit 1
         """},
    ],
    done("""
    No variables in a backend block, `init -migrate-state` (never `-reconfigure` when the state must survive),
    clean up the old local file, let a normal apply fix drift, and keep state out of Git: Module 8 in one vault. ⚒
    """),
    setup="""
    mkdir -p $R/yard8 && cd $R/yard8
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "random_pet" "ship" {}
    ''') + hcl("variables.tf", '''
    variable "vault_path" {
      type    = string
      default = "vault/terraform.tfstate"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    terraform show -json | $PY -c "import json,sys; print([r['values']['id'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='random_pet.ship'][0])" > /tmp/yard8_pet
    """ + hcl("backend.tf", '''
    terraform {
      backend "local" {
        path = var.vault_path
      }
    }
    ''') + """
    echo "painted pink" > hull.txt
    git init -q . 2>/dev/null || true
    """,
)

# 9.1 · inspecting state ---------------------------------------------------------------------------------------------
tf_lab(
    "the-index",
    "🟢 Terraform # · The index",
    "Read outputs and attributes the way scripts do: output -raw and state show.",
    f"""
    # The index

    In `/root/index`, Terraform built a hull and a ship with a random name. A script on the dock needs two facts
    from the ledger, and it can't cope with quotes.

    Lesson: {L("9.1", "Inspecting state")}
    """,
    [
        {"title": "The ship's name, raw",
         "text": """
         Write the value of the output `ship` into `/root/index/name.txt`, **without quotes**, using a terraform command
         (no copy-paste, no editing the state).
         """,
         "hint": "`terraform output ship` prints it with quotes; `terraform output -raw ship > name.txt` doesn't.",
         "solve": "cd $R/index\nterraform output -raw ship > name.txt",
         "wrong": "cd $R/index\nterraform output ship > name.txt",
         "verify": """
         cd $R/index
         [ "$(cat name.txt 2>/dev/null)" = "$(attr . random_pet.ship id)" ] || exit 1
         """},
        {"title": "One attribute",
         "text": """
         What `file_permission` does `local_file.hull` have in the state? Write the value alone into `/root/index/perm.txt`.
         """,
         "hint": "`terraform state show local_file.hull` lists every attribute of that one resource.",
         "solve": "cd $R/index\nterraform state show -no-color local_file.hull\nterraform show -json | $PY -c \"import json,sys; print([r['values']['file_permission'] for r in json.load(sys.stdin)['values']['root_module']['resources'] if r['address']=='local_file.hull'][0])\" > perm.txt",
         "wrong": "cd $R/index\necho 0644 > perm.txt",
         "verify": """
         cd $R/index
         [ "$(tr -d ' \\n\\r"' < perm.txt 2>/dev/null)" = "$(attr . local_file.hull file_permission)" ] || exit 1
         """},
    ],
    done("""
    `terraform state list` is the index, `state show ADDRESS` one page, `terraform show` everything, and
    `terraform output -raw NAME` one value the way scripts want it. Named and `-json` outputs print sensitive values.
    """, "Terraform · The stray ship"),
    setup="""
    mkdir -p $R/index && cd $R/index
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "random_pet" "ship" {}

    output "ship" {
      value = random_pet.ship.id
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 9.2 · import -----------------------------------------------------------------------------------------------------------
tf_lab(
    "stray-ship",
    "🟡 Terraform # · The stray ship",
    "Adopt existing objects: an import block with generated config, then the terraform import command.",
    f"""
    # The stray ship

    Two dock codes already exist: someone made them by hand. Terraform must adopt them **with their current values**.
    The random provider lets you import a `random_string` by giving its value as the ID.

    Lesson: {L("9.2", "Importing existing infrastructure")}
    """,
    [
        {"title": "With an import block",
         "text": """
         In `/root/stray`, adopt the code `Kestrel42` as **`random_string.code`**:

         - write an `import` block, and let Terraform write the resource block (`-generate-config-out=generated.tf`)
         - clean the generated file: no `= null` lines left
         - apply. `random_string.code` must have the result `Kestrel42`, and the plan must end with **No changes**
         """,
         "hint": "`import { to = random_string.code  id = \"Kestrel42\" }` in import.tf, then `terraform plan -generate-config-out=generated.tf`, `sed -i '/= null/d' generated.tf`, `terraform apply`.",
         "solve": """cd $R/stray
cat > import.tf <<'HCL'
import {
  to = random_string.code
  id = "Kestrel42"
}
HCL
terraform plan -generate-config-out=generated.tf
sed -i '/= null/d' generated.tf
terraform apply -auto-approve""",
         "wrong": """cd $R/stray
cat > code.tf <<'HCL'
resource "random_string" "code" {
  length = 9
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/stray
         [ "$(attr . random_string.code result)" = "Kestrel42" ] || exit 1
         ! grep -q '= null' *.tf || exit 1
         noplan . || exit 1
         """},
        {"title": "The old command",
         "text": """
         A second code exists: `Osprey7`. Adopt it as **`random_string.osprey`**, this time with the
         **`terraform import`** command. It needs the resource block first (`length = 7`).

         The plan must end with **No changes**.
         """,
         "hint": "Write `resource \"random_string\" \"osprey\" { length = 7 }`, then `terraform import random_string.osprey Osprey7`. One resource per command, and no plan before it.",
         "solve": """cd $R/stray
cat > osprey.tf <<'HCL'
resource "random_string" "osprey" {
  length = 7
}
HCL
terraform import random_string.osprey Osprey7
terraform plan""",
         "wrong": """cd $R/stray
cat > osprey.tf <<'HCL'
resource "random_string" "osprey" {
  length = 7
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/stray
         [ "$(attr . random_string.osprey result)" = "Osprey7" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    An import block + `-generate-config-out` gives you a plan, many imports at once and a record in code; clean the
    generated file before you keep it. `terraform import` does one resource, needs the block first, and shows no plan.
    Not every resource supports import: check the registry docs.
    """, "Terraform · New names"),
    setup="""
    mkdir -p $R/stray && cd $R/stray
    """ + hcl("versions.tf", '''
    terraform {
      required_providers {
        random = {
          source = "hashicorp/random"
        }
      }
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# 9.3 · moved ------------------------------------------------------------------------------------------------------------
tf_lab(
    "new-names",
    "🟡 Terraform # · New names",
    "Rename a resource and switch count to for_each with moved blocks, without rebuilding anything.",
    f"""
    # New names

    In `/root/names`, the hull and two bunks are built. The team wants better names, and the bunks keyed by crew
    member. Nothing real may be rebuilt: Terraform must only learn the new addresses.

    Lesson: {L("9.3", "Renaming with moved")}
    """,
    [
        {"title": "The main hull",
         "text": """
         Rename `local_file.hull` to **`local_file.main_hull`** in the code, with a record that other environments
         can apply too. Apply: the hull must not be rebuilt, and the plan must end with **No changes**.
         """,
         "hint": "Rename the block, then add `moved { from = local_file.hull  to = local_file.main_hull }` and apply. `terraform state mv` would work here, but leaves no record in the code.",
         "solve": """cd $R/names
sed -i 's/resource "local_file" "hull"/resource "local_file" "main_hull"/' main.tf
cat >> main.tf <<'HCL'

moved {
  from = local_file.hull
  to   = local_file.main_hull
}
HCL
terraform apply -auto-approve""",
         "wrong": """cd $R/names
sed -i 's/resource "local_file" "hull"/resource "local_file" "main_hull"/' main.tf
terraform state mv local_file.hull local_file.main_hull""",
         "verify": """
         cd $R/names
         grep -q '^moved' main.tf || exit 1
         st . | grep -qx local_file.main_hull || exit 1
         ! st . | grep -qx local_file.hull || exit 1
         [ "$(stat -c %Y hull.txt)" = "1577836800" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "Bunks by name",
         "text": """
         Switch `local_file.bunk` from `count` to **`for_each = toset(var.crew)`**, keyed by name
         (`bunk["Ada"]`, `bunk["Bo"]`). Same files, nothing rebuilt, plan: **No changes**.
         """,
         "hint": "Keep the filename `bunk-<name>.txt` and the content. Add one moved block per bunk: `from = local_file.bunk[0]  to = local_file.bunk[\"Ada\"]`, and [1] → [\"Bo\"].",
         "solve": """cd $R/names
$PY - <<'PY'
import re
t=open('main.tf').read()
new='''resource "local_file" "bunk" {
  for_each = toset(var.crew)
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.key}"
}

moved {
  from = local_file.bunk[0]
  to   = local_file.bunk["Ada"]
}

moved {
  from = local_file.bunk[1]
  to   = local_file.bunk["Bo"]
}'''
t=re.sub(r'resource "local_file" "bunk" \\{.*?\\n\\}', new, t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "wrong": """cd $R/names
$PY - <<'PY'
import re
t=open('main.tf').read()
new='''resource "local_file" "bunk" {
  for_each = toset(var.crew)
  filename = "${path.module}/bunk-${each.key}.txt"
  content  = "Bunk of ${each.key}"
}'''
t=re.sub(r'resource "local_file" "bunk" \\{.*?\\n\\}', new, t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/names
         st . | grep -qx 'local_file.bunk\\["Ada"\\]' || exit 1
         st . | grep -qx 'local_file.bunk\\["Bo"\\]' || exit 1
         [ "$(stat -c %Y bunk-Ada.txt)" = "1577836800" ] && [ "$(stat -c %Y bunk-Bo.txt)" = "1577836800" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Terraform only sees addresses: a rename alone is destroy + create. A `moved` block changes the address and keeps
    the real object, with a plan and a record every environment can apply. Keep moved blocks until all have applied them.
    """, "Terraform · Hand over"),
    setup="""
    mkdir -p $R/names && cd $R/names
    """ + hcl("main.tf", '''
    variable "crew" {
      type    = list(string)
      default = ["Ada", "Bo"]
    }

    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "local_file" "bunk" {
      count    = length(var.crew)
      filename = "${path.module}/bunk-${var.crew[count.index]}.txt"
      content  = "Bunk of ${var.crew[count.index]}"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    touch -d @1577836800 hull.txt bunk-Ada.txt bunk-Bo.txt 2>/dev/null || true
    """,
)

# 9.4 + 9.5 · removed and logging -----------------------------------------------------------------------------------------
tf_lab(
    "hand-over",
    "🟡 Terraform # · Hand over",
    "Stop managing a resource without destroying it, then keep a debug log of a plan.",
    f"""
    # Hand over

    In `/root/handover`, the logbook belongs to another team from today. Terraform must let go of it, and the
    file must stay exactly where it is. Then the other team asks for a debug log.

    Lessons: {L("9.4", "Letting go with removed")} · {L("9.5", "Verbose logging")}
    """,
    [
        {"title": "Let go of the logbook",
         "text": """
         Make Terraform **stop managing** `local_file.logbook` without deleting `logbook.txt`, with a plan you can review.
         Remove its resource block. Plan: **No changes** at the end, and `logbook.txt` still there.
         """,
         "hint": "Replace the resource block with `removed { from = local_file.logbook  lifecycle { destroy = false } }`, then `terraform apply`. Just deleting the block would destroy the file.",
         "solve": """cd $R/handover
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'resource "local_file" "logbook" \\{.*?\\n\\}', 'removed {\\n  from = local_file.logbook\\n\\n  lifecycle {\\n    destroy = false\\n  }\\n}', t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "wrong": """cd $R/handover
$PY - <<'PY'
import re
t=open('main.tf').read()
t=re.sub(r'resource "local_file" "logbook" \\{.*?\\n\\}', '', t, flags=re.S)
open('main.tf','w').write(t)
PY
terraform apply -auto-approve""",
         "verify": """
         cd $R/handover
         [ "$(cat logbook.txt 2>/dev/null)" = "every voyage" ] || exit 1
         ! st . | grep -q 'local_file.logbook' || exit 1
         ! grep -q 'resource "local_file" "logbook"' main.tf || exit 1
         grep -q '^removed' main.tf || exit 1
         noplan . || exit 1
         """},
        {"title": "The foreman's diary",
         "text": """
         Save a **DEBUG** log of `terraform plan` into `/root/handover/plan.log`, using Terraform's own logging.
         """,
         "hint": "Two environment variables: `TF_LOG=DEBUG TF_LOG_PATH=./plan.log terraform plan`. TF_LOG_PATH alone logs nothing.",
         "solve": "cd $R/handover\nTF_LOG=DEBUG TF_LOG_PATH=./plan.log terraform plan",
         "wrong": "cd $R/handover\nTF_LOG_PATH=./plan.log terraform plan",
         "verify": """
         cd $R/handover
         grep -q '\\[DEBUG\\]' plan.log 2>/dev/null || exit 1
         grep -q 'Terraform version' plan.log || exit 1
         """},
    ],
    done("""
    Deleting a block destroys the real object; `removed` with `destroy = false` only lets go. `TF_LOG` turns the logs
    on (TRACE → ERROR) and `TF_LOG_PATH` keeps them in a file. Logs can contain secrets.
    """, "Terraform · Four doors"),
    setup="""
    mkdir -p $R/handover && cd $R/handover
    """ + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "local_file" "logbook" {
      filename = "${path.module}/logbook.txt"
      content  = "every voyage"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    """,
)

# 9.6 · reading errors ------------------------------------------------------------------------------------------------------
tf_lab(
    "four-doors",
    "🔧 Terraform # · Four doors",
    "A language error, a cycle and a provider error: read each one and fix it at the right door.",
    f"""
    # Four doors

    The blueprint in `/root/doors` won't validate. Read every error: is it language, state, core or provider?

    Lesson: {L("9.6", "Reading errors")}
    """,
    [
        {"title": "Language and core",
         "text": """
         Make `terraform validate` succeed and apply. The goal: `orders.txt` says `build 3 masts`, and both
         `crew.txt` and `log.txt` copy the **orders**.
         """,
         "hint": "Validate shows a typo (Did you mean \\\"filename\\\"?) and an `Error: Cycle`: crew reads the log and the log reads the crew. Point both at `local_file.orders.content`.",
         "solve": """cd $R/doors
sed -i 's/filname/filename/' main.tf
sed -i 's/local_file.log.content/local_file.orders.content/; s/local_file.crew.content/local_file.orders.content/' main.tf
terraform validate
terraform apply -auto-approve""",
         "wrong": "cd $R/doors\nsed -i 's/filname/filename/' main.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/doors
         terraform validate >/dev/null 2>&1 || exit 1
         for f in orders crew log; do [ "$(cat $f.txt 2>/dev/null)" = "build 3 masts" ] || exit 1; done
         noplan . || exit 1
         """},
        {"title": "The supplier's door",
         "background": """
         cd $R/doors
         mkdir -p hull.txt/old
         cat >> main.tf <<'HCL'

         resource "local_file" "hull" {
           filename = "${path.module}/hull.txt"
           content  = "oak"
         }
         HCL
         sed -i 's/^         //' main.tf
         """,
         "text": """
         Someone added `local_file.hull`. Validate passes, but `terraform apply` fails. Read the error: which door is it?

         The folder `hull.txt/` is an old leftover nobody needs. Fix it so `hull.txt` is a file saying `oak`,
         and the plan ends with **No changes**. The resource keeps its filename.
         """,
         "hint": "`Error: Create local file error ... is a directory` comes from the provider: the real world is in the way. Remove the folder (`rm -rf hull.txt`) and apply again.",
         "solve": "cd $R/doors\nterraform apply -auto-approve || true\nrm -rf hull.txt\nterraform apply -auto-approve",
         "wrong": "cd $R/doors\nsed -i 's|/hull.txt\"|/hull2.txt\"|' main.tf\nterraform apply -auto-approve",
         "verify": """
         cd $R/doors
         [ -f hull.txt ] && [ "$(cat hull.txt)" = "oak" ] || exit 1
         grep -q '/hull.txt"' main.tf || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    Language errors (validate catches them), state errors (locks, backends), core errors (`Error: Cycle`) and provider
    errors (bad values at plan, the real world at apply). The first line says what, `on main.tf line N` says where.
    """, "BOSS · The audit"),
    setup="""
    mkdir -p $R/doors && cd $R/doors
    """ + hcl("main.tf", '''
    resource "local_file" "orders" {
      filname = "${path.module}/orders.txt"
      content = "build 3 masts"
    }

    resource "local_file" "crew" {
      filename = "${path.module}/crew.txt"
      content  = local_file.log.content
    }

    resource "local_file" "log" {
      filename = "${path.module}/log.txt"
      content  = local_file.crew.content
    }
    ''') + """
    terraform init -input=false >/dev/null
    """,
)

# boss (9.R) ---------------------------------------------------------------------------------------------------------------
tf_lab(
    "the-audit",
    "🔴 Terraform BOSS · The audit",
    "Import, rename, hand over and fix, without rebuilding or deleting anything. Only the goal is given.",
    f"""
    # 🔴 BOSS · The audit

    The auditors are coming to `/root/audit`. Someone renamed things, someone deleted a block, someone made a dock
    code by hand, and the code doesn't validate. You only get the **goal**.

    Covers Module 9: {L("9.2", "import")} · {L("9.3", "moved")} · {L("9.4", "removed")} · {L("9.6", "errors")}
    """,
    [
        {"title": "Pass the audit",
         "text": """
         In `/root/audit`, reach this state:
         - `terraform validate` succeeds and `terraform plan` says **No changes**
         - the hull is managed as **`local_file.main_hull`**, and `hull.txt` was **not rebuilt**
         - the logbook is **no longer managed** by Terraform, and `logbook.txt` still exists
         - the dock code `Kestrel42` (made by hand) is managed as **`random_string.code`** with that exact value
         """,
         "hint": "Validate first (a typo). Then: a moved block for the rename, a removed block (destroy = false) for the logbook, an import block (plus a resource block with length = 9, or generated config) for the code.",
         "solve": """cd $R/audit
sed -i 's/contnet/content/' main.tf
cat >> main.tf <<'HCL'

moved {
  from = local_file.hull
  to   = local_file.main_hull
}

removed {
  from = local_file.logbook

  lifecycle {
    destroy = false
  }
}

import {
  to = random_string.code
  id = "Kestrel42"
}

resource "random_string" "code" {
  length = 9
}
HCL
terraform validate
terraform apply -auto-approve""",
         "wrong": """cd $R/audit
sed -i 's/contnet/content/' main.tf
cat >> main.tf <<'HCL'

removed {
  from = local_file.logbook

  lifecycle {
    destroy = false
  }
}

import {
  to = random_string.code
  id = "Kestrel42"
}

resource "random_string" "code" {
  length = 9
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/audit
         terraform validate >/dev/null 2>&1 || exit 1
         s=$(st .)
         echo "$s" | grep -qx local_file.main_hull || exit 1
         ! echo "$s" | grep -qx local_file.hull || exit 1
         ! echo "$s" | grep -q logbook || exit 1
         [ "$(cat logbook.txt 2>/dev/null)" = "every voyage" ] || exit 1
         [ "$(stat -c %Y hull.txt)" = "1577836800" ] || exit 1
         [ "$(attr . random_string.code result)" = "Kestrel42" ] || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    `moved` for the new name, `removed` with `destroy = false` to let go, an import block to adopt, and validate
    to find the typo first: Terraform's view of the world changed, and the world didn't. Module 9 in one audit. ⚒
    """),
    setup="""
    mkdir -p $R/audit && cd $R/audit
    """ + hcl("versions.tf", '''
    terraform {
      required_providers {
        local = {
          source = "hashicorp/local"
        }
        random = {
          source = "hashicorp/random"
        }
      }
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "hull" {
      filename = "${path.module}/hull.txt"
      content  = "oak, 3 masts"
    }

    resource "local_file" "logbook" {
      filename = "${path.module}/logbook.txt"
      content  = "every voyage"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    touch -d @1577836800 hull.txt 2>/dev/null || true
    """ + hcl("main.tf", '''
    resource "local_file" "main_hull" {
      filename = "${path.module}/hull.txt"
      contnet  = "oak, 3 masts"
    }
    ''') + """
    """,
)

DOCK_MODULE = hcl("modules/dock/variables.tf", '''
    variable "name" {
      type        = string
      description = "Ship name"
    }

    variable "masts" {
      type    = number
      default = 1
    }
    ''') + hcl("modules/dock/main.tf", '''
    resource "local_file" "this" {
      filename = "${path.root}/dock-${var.name}.txt"
      content  = "${var.name}: ${var.masts} masts"
    }
    ''') + hcl("modules/dock/outputs.tf", '''
    output "file" {
      value = local_file.this.filename
    }
    ''')

# 10.1 + 10.2 · calling a module -------------------------------------------------------------------------------------
tf_lab(
    "first-kit",
    "🟢 Terraform # · First kit",
    "Call a child module with a module block, then read its output from the root.",
    f"""
    # First kit

    In `/root/kit`, the dock kit is ready in `modules/dock` (inputs `name` and `masts`, output `file`).
    The root module (`main.tf`) is still empty.

    Lessons: {L("10.1", "What a module is")} · {L("10.2", "Calling a module")}
    """,
    [
        {"title": "Order a dock",
         "text": """
         In `main.tf`, call the dock module as **`kestrel`** with `name = "kestrel"` and `masts = 3`, and apply.

         `dock-kestrel.txt` must say `kestrel: 3 masts`, and the state must list `module.kestrel.local_file.this`.
         """,
         "hint": "`module \"kestrel\" { source = \"./modules/dock\"  name = \"kestrel\"  masts = 3 }`. A new module call needs `terraform init` first.",
         "solve": """cd $R/kit
cat > main.tf <<'HCL'
module "kestrel" {
  source = "./modules/dock"
  name   = "kestrel"
  masts  = 3
}
HCL
terraform init
terraform apply -auto-approve""",
         "wrong": """cd $R/kit
cat > main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/dock-kestrel.txt"
  content  = "kestrel: 3 masts"
}
HCL
terraform init
terraform apply -auto-approve""",
         "verify": """
         cd $R/kit
         st . | grep -qx module.kestrel.local_file.this || exit 1
         [ "$(cat dock-kestrel.txt 2>/dev/null)" = "kestrel: 3 masts" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "Read the receipt",
         "text": """
         Add a root output **`kestrel_file`** that returns the module's `file` output, and apply.
         `terraform output -raw kestrel_file` must print `./dock-kestrel.txt`.
         """,
         "hint": "Module results are `module.LABEL.OUTPUT`: `output \"kestrel_file\" { value = module.kestrel.file }`. The resources inside the module aren't reachable from the root.",
         "solve": """cd $R/kit
cat >> main.tf <<'HCL'

output "kestrel_file" {
  value = module.kestrel.file
}
HCL
terraform apply -auto-approve
terraform output -raw kestrel_file""",
         "wrong": """cd $R/kit
cat >> main.tf <<'HCL'

output "kestrel_file" {
  value = module.kestrel.local_file.this.filename
}
HCL
terraform apply -auto-approve""",
         "verify": """
         cd $R/kit
         [ "$(terraform output -raw kestrel_file 2>/dev/null)" = "./dock-kestrel.txt" ] || exit 1
         grep -q 'module.kestrel.file' main.tf || exit 1
         """},
    ],
    done("""
    A module is a folder of .tf files; the root calls it with a `module` block (label, `source`, inputs) and needs
    `terraform init` for every new call. Resources inside get addresses like `module.kestrel.local_file.this`,
    and only outputs come back: `module.kestrel.file`.
    """, "Terraform · Sealed kit"),
    setup="""
    mkdir -p $R/kit/modules/dock && cd $R/kit
    """ + DOCK_MODULE + """
    echo '# call modules/dock here' > main.tf
    """,
)

# 10.4 · variable scope ------------------------------------------------------------------------------------------------
tf_lab(
    "sealed-kit",
    "🔧 Terraform # · Sealed kit",
    "A module can't see the root's variables, and the root can't see inside a module. Pass values in and out.",
    f"""
    # Sealed kit

    In `/root/sealed`, the root has `var.env`, and the dock module tries to use it. `terraform validate` fails.

    Lesson: {L("10.4", "Variable scope")}
    """,
    [
        {"title": "Through the order form",
         "text": """
         Make the module use the **root's** `var.env`: `dock-kestrel.txt` must say `prod: kestrel` and change with the
         root's value (`terraform plan -var env=dev` must want to change it). Apply.
         """,
         "hint": "Declare `variable \"env\" { type = string }` in modules/dock/variables.tf (no default), and pass `env = var.env` in the module block.",
         "solve": """cd $R/sealed
printf '\\nvariable "env" {\\n  type = string\\n}\\n' >> modules/dock/variables.tf
sed -i 's|  name   = "kestrel"|  name   = "kestrel"\\n  env    = var.env|' main.tf
terraform apply -auto-approve""",
         "wrong": """cd $R/sealed
printf '\\nvariable "env" {\\n  type    = string\\n  default = "prod"\\n}\\n' >> modules/dock/variables.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/sealed
         terraform validate >/dev/null 2>&1 || exit 1
         [ "$(cat dock-kestrel.txt 2>/dev/null)" = "prod: kestrel" ] || exit 1
         terraform plan -input=false -lock=false -detailed-exitcode -var env=dev >/dev/null 2>&1; [ $? -eq 2 ] || exit 1
         noplan . || exit 1
         """},
        {"title": "Through the receipt",
         "text": """
         The root needs the file's **content**. Add an output `content` in the module, and a root output
         **`kestrel_content`** that returns it. `terraform output -raw kestrel_content` must print `prod: kestrel`.
         """,
         "hint": "Module: `output \"content\" { value = local_file.this.content }`. Root: `output \"kestrel_content\" { value = module.kestrel.content }`.",
         "solve": """cd $R/sealed
printf '\\noutput "content" {\\n  value = local_file.this.content\\n}\\n' >> modules/dock/outputs.tf
printf '\\noutput "kestrel_content" {\\n  value = module.kestrel.content\\n}\\n' >> main.tf
terraform apply -auto-approve""",
         "wrong": """cd $R/sealed
printf '\\noutput "kestrel_content" {\\n  value = module.kestrel.local_file.this.content\\n}\\n' >> main.tf
terraform apply -auto-approve""",
         "verify": """
         cd $R/sealed
         [ "$(terraform output -raw kestrel_content 2>/dev/null)" = "prod: kestrel" ] || exit 1
         """},
    ],
    done("""
    Every module has its own variables: values go in explicitly (`env = var.env`) and only outputs come out.
    Locals and resources stay private. Providers are the exception: children inherit the root's.
    """, "Terraform · Kit sources"),
    setup="""
    mkdir -p $R/sealed/modules/dock && cd $R/sealed
    """ + hcl("modules/dock/variables.tf", '''
    variable "name" {
      type = string
    }
    ''') + hcl("modules/dock/main.tf", '''
    resource "local_file" "this" {
      filename = "${path.root}/dock-${var.name}.txt"
      content  = "${var.env}: ${var.name}"
    }
    ''') + hcl("modules/dock/outputs.tf", '''
    output "file" {
      value = local_file.this.filename
    }
    ''') + hcl("main.tf", '''
    variable "env" {
      type    = string
      default = "prod"
    }

    module "kestrel" {
      source = "./modules/dock"
      name   = "kestrel"
    }
    ''') + """
    terraform init -input=false >/dev/null 2>&1 || true
    """,
)

# 10.3 + 10.5 · sources and versions --------------------------------------------------------------------------------------
tf_lab(
    "kit-sources",
    "🟡 Terraform # · Kit sources",
    "Use a module from the public registry with a pinned version, upgrade it on purpose, then pin a Git copy with ?ref=.",
    f"""
    # Kit sources

    In `/root/sources` you'll use a real public module: **`cloudposse/label/null`**. It builds consistent names
    (`namespace-stage-name`) and creates no resources, so it runs anywhere.

    Lessons: {L("10.3", "Where modules come from")} · {L("10.5", "Versioning modules")}
    """,
    [
        {"title": "From the catalogue, pinned",
         "text": """
         Call it as module **`label`** from the registry, pinned to exactly version **`0.24.1`**, with
         `namespace = "sy"`, `stage = "prod"`, `name = "kestrel"`. Add a root output **`id`** = the module's `id`, and apply.

         `terraform output -raw id` must print `sy-prod-kestrel`.
         """,
         "hint": "`module \"label\" { source = \"cloudposse/label/null\"  version = \"0.24.1\" ... }` and `output \"id\" { value = module.label.id }`. Then init and apply.",
         "solve": """cd $R/sources
cat > main.tf <<'HCL'
module "label" {
  source    = "cloudposse/label/null"
  version   = "0.24.1"
  namespace = "sy"
  stage     = "prod"
  name      = "kestrel"
}

output "id" {
  value = module.label.id
}
HCL
terraform init
terraform apply -auto-approve""",
         "wrong": """cd $R/sources
cat > main.tf <<'HCL'
module "label" {
  source    = "cloudposse/label/null"
  namespace = "sy"
  stage     = "prod"
  name      = "kestrel"
}

output "id" {
  value = module.label.id
}
HCL
terraform init
terraform apply -auto-approve""",
         "verify": """
         cd $R/sources
         [ "$(terraform output -raw id 2>/dev/null)" = "sy-prod-kestrel" ] || exit 1
         $PY -c "import json,sys; m=[x for x in json.load(open('.terraform/modules/modules.json'))['Modules'] if x['Key']=='label']; sys.exit(0 if m and m[0].get('Version')=='0.24.1' else 1)" || exit 1
         """},
        {"title": "Upgrade on purpose, pin Git",
         "text": """
         1. Move `label` to exactly **`0.25.0`** (plan first: what does Terraform say?), and install it.
         2. Add a second copy from **Git**: module **`label_git`** with source
            `git::https://github.com/cloudposse/terraform-null-label.git`, pinned to the tag `0.25.0`,
            `namespace = "sy"`, `stage = "dev"`, `name = "kestrel"`, and a root output **`dev_id`**.

         Apply. `terraform output -raw dev_id` must print `sy-dev-kestrel`.
         """,
         "hint": "After changing `version`, `terraform init -upgrade` installs it. Git modules have no version argument: add `?ref=0.25.0` to the source URL.",
         "solve": """cd $R/sources
sed -i 's/version   = "0.24.1"/version   = "0.25.0"/' main.tf
cat >> main.tf <<'HCL'

module "label_git" {
  source    = "git::https://github.com/cloudposse/terraform-null-label.git?ref=0.25.0"
  namespace = "sy"
  stage     = "dev"
  name      = "kestrel"
}

output "dev_id" {
  value = module.label_git.id
}
HCL
terraform init -upgrade
terraform apply -auto-approve""",
         "wrong": """cd $R/sources
sed -i 's/version   = "0.24.1"/version   = "0.25.0"/' main.tf
cat >> main.tf <<'HCL'

module "label_git" {
  source    = "git::https://github.com/cloudposse/terraform-null-label.git"
  namespace = "sy"
  stage     = "dev"
  name      = "kestrel"
}

output "dev_id" {
  value = module.label_git.id
}
HCL
terraform init -upgrade
terraform apply -auto-approve""",
         "verify": """
         cd $R/sources
         [ "$(terraform output -raw dev_id 2>/dev/null)" = "sy-dev-kestrel" ] || exit 1
         $PY -c "
import json,sys
m={x['Key']:x for x in json.load(open('.terraform/modules/modules.json'))['Modules']}
ok=m.get('label',{}).get('Version')=='0.25.0' and '?ref=0.25.0' in m.get('label_git',{}).get('Source','')
sys.exit(0 if ok else 1)" || exit 1
         """},
    ],
    done("""
    Registry modules use `NAMESPACE/NAME/PROVIDER` and a `version`; Git modules pin with `?ref=`. `terraform init`
    downloads them into `.terraform/modules`, and `init -upgrade` moves to a newer allowed version, on purpose.
    The lock file doesn't pin modules.
    """, "Terraform · Fleet kit"),
    setup="""
    mkdir -p $R/sources && cd $R/sources
    echo '# use cloudposse/label/null here' > main.tf
    """,
)

# 10.7 · writing your own module -------------------------------------------------------------------------------------------
tf_lab(
    "fleet-kit",
    "🟡 Terraform # · Fleet kit",
    "Turn copy-pasted resources into your own module called with for_each, without rebuilding them, then add validation.",
    f"""
    # Fleet kit

    In `/root/fleet`, three `local_file` blocks are the same code, copy-pasted: `mast_kestrel`, `mast_osprey`,
    `mast_wren`. They're already built. Time for a kit.

    Lesson: {L("10.7", "Writing your own module")}
    """,
    [
        {"title": "Make the kit",
         "text": """
         Create **`modules/mast`** (variables `name` and `masts`, the resource, an output `file`) and call it **once**
         with `for_each = var.fleet` (the map is in `variables.tf`). Keep the same filenames and contents.

         The three files must **not be rebuilt**, and no `local_file` block may stay in the root. Plan: **No changes**.
         """,
         "hint": "Module resource: `local_file \"this\"` with `filename = \"${path.root}/mast-${var.name}.txt\"`, `content = \"${var.name}: ${var.masts} masts\"`. Root: `module \"mast\" { source = \"./modules/mast\"  for_each = var.fleet  name = each.key  masts = each.value }`. Then a moved block per file: `from = local_file.mast_kestrel  to = module.mast[\"kestrel\"].local_file.this`.",
         "solve": """cd $R/fleet
mkdir -p modules/mast
cat > modules/mast/variables.tf <<'HCL'
variable "name" {
  type        = string
  description = "Ship name"
}

variable "masts" {
  type        = number
  description = "Number of masts"
}
HCL
cat > modules/mast/main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/mast-${var.name}.txt"
  content  = "${var.name}: ${var.masts} masts"
}
HCL
cat > modules/mast/outputs.tf <<'HCL'
output "file" {
  value = local_file.this.filename
}
HCL
cat > main.tf <<'HCL'
module "mast" {
  source   = "./modules/mast"
  for_each = var.fleet
  name     = each.key
  masts    = each.value
}

moved {
  from = local_file.mast_kestrel
  to   = module.mast["kestrel"].local_file.this
}

moved {
  from = local_file.mast_osprey
  to   = module.mast["osprey"].local_file.this
}

moved {
  from = local_file.mast_wren
  to   = module.mast["wren"].local_file.this
}
HCL
terraform init
terraform apply -auto-approve""",
         "wrong": """cd $R/fleet
mkdir -p modules/mast
cat > modules/mast/variables.tf <<'HCL'
variable "name" {
  type = string
}

variable "masts" {
  type = number
}
HCL
cat > modules/mast/main.tf <<'HCL'
resource "local_file" "this" {
  filename = "${path.root}/mast-${var.name}.txt"
  content  = "${var.name}: ${var.masts} masts"
}
HCL
cat > main.tf <<'HCL'
module "mast" {
  source   = "./modules/mast"
  for_each = var.fleet
  name     = each.key
  masts    = each.value
}
HCL
terraform init
terraform apply -auto-approve""",
         "verify": """
         cd $R/fleet
         [ -f modules/mast/variables.tf ] && [ -f modules/mast/outputs.tf ] || exit 1
         ! grep -q 'resource "local_file"' main.tf || exit 1
         for s in kestrel osprey wren; do
           st . | grep -qx "module.mast\\[\\"$s\\"\\].local_file.this" || exit 1
           [ "$(stat -c %Y mast-$s.txt)" = "1577836800" ] || exit 1
         done
         [ "$(cat mast-osprey.txt)" = "osprey: 2 masts" ] || exit 1
         noplan . || exit 1
         """},
        {"title": "Inspect the order",
         "text": """
         A good kit rejects bad orders. Add a **validation** to the module's `masts` variable: 1 to 5.

         `terraform plan -var 'fleet={"kestrel"=9}'` must fail with `Invalid value for variable`, and the normal plan
         must still say **No changes**.
         """,
         "hint": "Inside `variable \"masts\"` in modules/mast/variables.tf: `validation { condition = var.masts >= 1 && var.masts <= 5  error_message = \"A ship has 1 to 5 masts.\" }`.",
         "solve": """cd $R/fleet
$PY - <<'PY'
t=open('modules/mast/variables.tf').read()
t=t.replace('description = "Number of masts"','description = "Number of masts"\\n\\n  validation {\\n    condition     = var.masts >= 1 && var.masts <= 5\\n    error_message = "A ship has 1 to 5 masts."\\n  }')
open('modules/mast/variables.tf','w').write(t)
PY
terraform plan -var 'fleet={"kestrel"=9}' || true""",
         "wrong": """cd $R/fleet
$PY - <<'PY'
t=open('variables.tf').read()
t=t.replace('type = map(number)','type = map(number)\\n\\n  validation {\\n    condition     = length(var.fleet) <= 5\\n    error_message = "Too many ships."\\n  }')
open('variables.tf','w').write(t)
PY""",
         "verify": """
         cd $R/fleet
         terraform plan -input=false -lock=false -no-color -var 'fleet={"kestrel"=9}' 2>&1 | grep -q 'Invalid value for variable' || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A module is main + variables + outputs (+ a README). `for_each` on the module block builds a fleet from one kit,
    `moved` blocks carry existing resources inside without a rebuild, and validation in the module protects every caller.
    """, "BOSS · Kit yard"),
    setup="""
    mkdir -p $R/fleet && cd $R/fleet
    """ + hcl("variables.tf", '''
    variable "fleet" {
      type = map(number)
      default = {
        kestrel = 3
        osprey  = 2
        wren    = 1
      }
    }
    ''') + hcl("main.tf", '''
    resource "local_file" "mast_kestrel" {
      filename = "${path.root}/mast-kestrel.txt"
      content  = "kestrel: 3 masts"
    }

    resource "local_file" "mast_osprey" {
      filename = "${path.root}/mast-osprey.txt"
      content  = "osprey: 2 masts"
    }

    resource "local_file" "mast_wren" {
      filename = "${path.root}/mast-wren.txt"
      content  = "wren: 1 masts"
    }
    ''') + """
    terraform init -input=false >/dev/null && terraform apply -auto-approve -input=false >/dev/null
    touch -d @1577836800 mast-kestrel.txt mast-osprey.txt mast-wren.txt 2>/dev/null || true
    """,
)

# boss (10.R) -------------------------------------------------------------------------------------------------------------
tf_lab(
    "kit-yard",
    "🔴 Terraform BOSS · Kit yard",
    "Four module mistakes between a local kit and a registry kit. Only the goal is given.",
    f"""
    # 🔴 BOSS · Kit yard

    The yard in `/root/kityard` uses a local dock kit and a registry naming kit. It won't even initialise.
    You only get the **goal**.

    Covers Module 10: {L("10.2", "calling")} · {L("10.3", "sources")} · {L("10.4", "scope")} · {L("10.5", "versions")}
    """,
    [
        {"title": "Open the kit yard",
         "text": """
         In `/root/kityard`, reach this state:
         - `terraform init` and `terraform validate` succeed, and `terraform plan` says **No changes**
         - `dock-kestrel.txt` says `kestrel: 3 masts`
         - `terraform output -raw dock_file` prints `./dock-kestrel.txt`
         - `terraform output -raw label_id` prints `sy-prod-kestrel`, from `cloudposse/label/null` pinned to exactly **0.25.0**
         """,
         "hint": "Look for: a variable in a module source, a version on a local module, a missing required input, and an output that reaches inside a module.",
         "solve": """cd $R/kityard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('source  = var.label_source','source  = "cloudposse/label/null"')
t=t.replace('  version = "1.0.0"\\n','')
t=t.replace('  masts  = 3','  name   = "kestrel"\\n  masts  = 3')
t=t.replace('module.dock.local_file.this.filename','module.dock.file')
open('main.tf','w').write(t)
PY
terraform init
terraform validate
terraform apply -auto-approve""",
         "wrong": """cd $R/kityard
$PY - <<'PY'
t=open('main.tf').read()
t=t.replace('source  = var.label_source','source  = "cloudposse/label/null"')
t=t.replace('  version = "1.0.0"\\n','')
t=t.replace('  masts  = 3','  name   = "kestrel"\\n  masts  = 3')
t=t.replace('module.dock.local_file.this.filename','module.dock.file')
t=t.replace('version   = "0.25.0"','version   = ">= 0.24.0"')
open('main.tf','w').write(t)
PY
terraform init
terraform apply -auto-approve""",
         "verify": """
         cd $R/kityard
         terraform validate >/dev/null 2>&1 || exit 1
         [ "$(cat dock-kestrel.txt 2>/dev/null)" = "kestrel: 3 masts" ] || exit 1
         [ "$(terraform output -raw dock_file 2>/dev/null)" = "./dock-kestrel.txt" ] || exit 1
         [ "$(terraform output -raw label_id 2>/dev/null)" = "sy-prod-kestrel" ] || exit 1
         grep -Eq 'version += "0\\.25\\.0"' main.tf || exit 1
         noplan . || exit 1
         """},
    ],
    done("""
    A literal `source`, `version` only for registry modules (pinned exactly), every required input passed, and
    results read through outputs: Module 10 in one kit yard. ⚒
    """),
    setup="""
    mkdir -p $R/kityard/modules/dock && cd $R/kityard
    """ + DOCK_MODULE + hcl("main.tf", '''
    variable "label_source" {
      type    = string
      default = "cloudposse/label/null"
    }

    module "dock" {
      source  = "./modules/dock"
      version = "1.0.0"
      masts  = 3
    }

    module "label" {
      source  = var.label_source
      version   = "0.25.0"
      namespace = "sy"
      stage     = "prod"
      name      = "kestrel"
    }

    output "dock_file" {
      value = module.dock.local_file.this.filename
    }

    output "label_id" {
      value = module.label.id
    }
    ''') + """
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
         "6.6": "crate", "6.R": "fleet-yard",
         "7.1": "hidden-orders", "7.2": "shipyard-rules", "7.3": "shipyard-rules", "7.4": "timber-change",
         "7.5": "order-inspector", "7.6": "order-inspector", "7.7": "lookout", "7.8": "lookout", "7.R": "dock-rules",
         "8.1": "ledger-reading", "8.2": "ledger-reading", "8.4": "harbor-vault", "8.5": "harbor-vault",
         "8.6": "pink-hull", "8.7": "pink-hull", "8.9": "slipways", "8.R": "the-vault",
         "9.1": "the-index", "9.2": "stray-ship", "9.3": "new-names", "9.4": "hand-over", "9.5": "hand-over",
         "9.6": "four-doors", "9.R": "the-audit",
         "10.1": "first-kit", "10.2": "first-kit", "10.3": "kit-sources", "10.4": "sealed-kit", "10.5": "kit-sources",
         "10.6": "kit-sources", "10.7": "fleet-kit", "10.R": "kit-yard"}
with open(os.path.join(ROOT, "labs-terraform.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump({"_comment": "Terraform lesson code -> Killercoda lab URL (lab_links.py --course terraform)",
               **{k: KC + v for k, v in LINKS.items()}}, f, indent=2, ensure_ascii=False)
    f.write("\n")
print(f"wrote {len(ORDER)} Terraform labs in {TF}")
