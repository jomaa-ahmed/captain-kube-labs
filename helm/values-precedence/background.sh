#!/bin/bash
if ! command -v helm >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi
mkdir -p /root/charts
cd /root/charts
helm create harbor-web >/dev/null
sed -i 's/^appVersion:.*/appVersion: "1.27"/' harbor-web/Chart.yaml
sed -i 's/^description:.*/description: The harbor web page, packed for Captain Kube/' harbor-web/Chart.yaml
cd /root
cat > /root/prod-values.yaml <<'EOF'
replicaCount: 2
podLabels:
  team: harbor
EOF
touch /tmp/finished
