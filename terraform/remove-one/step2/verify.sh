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
cd $R/dismantle
[ -f teardown.tfplan ] || exit 1
n=$(terraform show -json teardown.tfplan | $PY -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for r in d.get('resource_changes',[]) if r['change']['actions']==['delete']))")
[ "$n" = "2" ] || exit 1
[ "$(tr -d ' \r\n' < $R/answers/destroy_count.txt 2>/dev/null)" = "2" ] || exit 1
s=$(st .)
echo "$s" | grep -qx local_file.hull && echo "$s" | grep -qx local_file.mast || exit 1
[ -f hull.txt ] && [ -f mast.txt ] || exit 1
