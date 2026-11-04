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
cd $R/yard
terraform validate >/dev/null 2>&1 || exit 1
s=$(st . | sort | tr '\n' ' ')
[ "$s" = 'data.archive_file.crate local_file.bunk["Ada"] local_file.bunk["Bo"] local_file.bunk["Cyrus"] local_file.manifest ' ] || exit 1
[ "$(cat bunk-Cyrus.txt 2>/dev/null)" = "Bunk of Cyrus" ] || exit 1
[ "$(cat manifest.txt 2>/dev/null)" = "PROD-KESTREL: 3 masts, flag violet" ] || exit 1
[ "$(echo 'local.label' | terraform console -var env=dev 2>/dev/null)" = '"DEV-KESTREL"' ] || exit 1
[ "$(echo 'local.masts' | terraform console -var env=dev 2>/dev/null)" = "1" ] || exit 1
[ "$(echo 'local.flag' | terraform console -var env=dev 2>/dev/null)" = '"grey"' ] || exit 1
$PY -c "import zipfile,sys; sys.exit(sorted(zipfile.ZipFile('crate.zip').namelist())!=['hull.txt','mast.txt'])" || exit 1
terraform output -json bunks 2>/dev/null | $PY -c "import json,sys,os; sys.exit(sorted(os.path.basename(f) for f in json.load(sys.stdin))!=['bunk-Ada.txt','bunk-Bo.txt','bunk-Cyrus.txt'])" || exit 1
noplan . || exit 1
