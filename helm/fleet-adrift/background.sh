#!/bin/bash
kubectl wait --for=condition=Ready node --all --timeout=300s >/dev/null
if ! command -v helm >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi
mkdir -p /root/charts
cd /root/charts
helm create harbor-web >/dev/null
sed -i 's/^appVersion:.*/appVersion: "1.27"/' harbor-web/Chart.yaml
sed -i 's/^description:.*/description: The harbor web page, packed for Captain Kube/' harbor-web/Chart.yaml
cd /root
kubectl create namespace armada >/dev/null
helm install ghost /root/charts/harbor-web -n armada --set image.tag=1.27-ghost >/dev/null
helm install beacon /root/charts/harbor-web -n armada --wait --timeout 5m >/dev/null
helm upgrade beacon /root/charts/harbor-web -n armada --set image.tag=1.27-tpyo >/dev/null
helm upgrade beacon /root/charts/harbor-web -n armada --set image.tag=1.27-tpyo,service.port=8080 >/dev/null
cat > /root/compass-prod.yaml <<'EOF'
replicaCount: 2
image:
  repository: nginx
  tag: "1.27-alpin"
podLabels:
  tier: nav
service:
  type: NodePort
  port: 80
EOF
helm install compass /root/charts/harbor-web -n armada -f /root/compass-prod.yaml >/dev/null
helm upgrade compass /root/charts/harbor-web -n armada --set replicaCount=1 >/dev/null
touch /tmp/finished
