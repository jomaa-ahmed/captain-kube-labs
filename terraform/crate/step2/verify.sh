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
         cd $R/crate
         md5sum -c /tmp/crate_md5 >/dev/null 2>&1 || exit 1
         $PY -c "
import zipfile,sys
z=zipfile.ZipFile('crate.zip')
ok=sorted(z.namelist())==['deck.txt','hull.txt','mast.txt','sail.txt'] and z.read('deck.txt')==b'Teak, scrubbed daily'
sys.exit(0 if ok else 1)" || exit 1
         noplan . || exit 1
