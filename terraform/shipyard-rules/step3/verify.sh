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
         cd $R/rules
         grep -q 'paint = var.paint' main.tf || exit 1
         terraform plan -var paint=red -input=false -detailed-exitcode -lock=false >/dev/null 2>&1 || exit 1
         terraform show -json | $PY -c "
import json,sys
d=json.load(sys.stdin)
r=[x for x in d['values']['root_module']['resources'] if x['address']=='terraform_data.hull'][0]
sys.exit(0 if r['values']['input']['paint']=='blue' else 1)" || exit 1
