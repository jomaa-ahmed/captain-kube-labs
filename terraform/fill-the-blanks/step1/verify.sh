#!/bin/bash
R=${LABROOT:-/root}; PY=${PY:-python3}
export TF_IN_AUTOMATION=1 TF_PLUGIN_CACHE_DIR=${TF_PLUGIN_CACHE_DIR:-$R/.terraform.d/plugin-cache}
mkdir -p "$TF_PLUGIN_CACHE_DIR"

st() { terraform -chdir="$1" state list 2>/dev/null; }
noplan() { terraform -chdir="$1" plan -input=false -detailed-exitcode -lock=false >/dev/null 2>&1; }
attr() {  # attr DIR ADDRESS ATTRIBUTE -> value from the state
  terraform -chdir="$1" show -json 2>/dev/null | $PY -c "
import json,sys
d=json.load(sys.stdin); a,k=sys.argv[1],sys.argv[2]
for r in d.get('values',{}).get('root_module',{}).get('resources',[]):
    if r['address']==a: print(r['values'].get(k,'')); break" "$2" "$3"; }
serial() { $PY -c "import json,sys; print(json.load(open(sys.argv[1]))['serial'])" "$1/terraform.tfstate" 2>/dev/null || echo 0; }
         cd $R/blanks
         $PY - <<'PY' || exit 1
import re,sys
t=open('variables.tf').read()
m=re.search(r'variable\s+"ship_name"\s*\{(.*?)\n\}', t, re.S)
ok = m and re.search(r'type\s*=\s*string', m.group(1)) and 'description' in m.group(1) and 'default' not in m.group(1)
sys.exit(0 if ok else 1)
PY
         ! grep -q 'Kestrel\|Osprey' main.tf || exit 1
         [ "$(grep -c 'var.ship_name' main.tf)" -ge 2 ] || exit 1
         [ "$(cat hull.txt)" = "Hull of the Osprey" ] && [ "$(cat flag.txt)" = "Flag of the Osprey" ] || exit 1
         noplan . || exit 1
