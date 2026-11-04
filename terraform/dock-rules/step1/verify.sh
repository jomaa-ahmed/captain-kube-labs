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
