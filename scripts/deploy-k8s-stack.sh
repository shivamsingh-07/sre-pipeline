#!/bin/bash

set -e

if ! helm version &>/dev/null; then
	echo "Helm is not installed!"
	exit 1
fi

if ! helm list -n vault | grep -q "vault"; then
	helm repo add hashicorp https://helm.releases.hashicorp.com
	helm install vault hashicorp/vault \
		--namespace vault \
		--create-namespace \
		--set server.dev.enabled=true \
		--set nodeSelector.type=dependent_services
fi

if ! helm list -n external-secrets | grep -q "external-secrets"; then
	helm repo add external-secrets https://charts.external-secrets.io
	helm install external-secrets external-secrets/external-secrets \
		--namespace external-secrets \
		--create-namespace \
		--set nodeSelector.type=dependent_services
fi

kubectl wait --for=condition=Ready pods --all -n external-secrets --timeout=180s
kubectl apply -f ../kubernetes/roles.yaml

kubectl wait --for=condition=Ready pods --all -n vault --timeout=180s

kubectl exec -i vault-0 -n vault -- vault auth enable kubernetes 2>/dev/null || true

kubectl exec -i vault-0 -n vault -- vault policy write student-app-policy - <<EOF
path "secret/data/student-app" {
  capabilities = ["read"]
}
EOF

kubectl exec -i vault-0 -n vault -- vault write auth/kubernetes/config \
	kubernetes_host="https://kubernetes.default.svc.cluster.local:443" \
	kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
	token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

kubectl exec -i vault-0 -n vault -- vault write auth/kubernetes/role/student-app \
	bound_service_account_names=vault-auth-sa \
	bound_service_account_namespaces=student-api \
	policies=student-app-policy \
	ttl=1h

kubectl exec -i vault-0 -n vault -- vault kv put secret/student-app \
	username="admin" \
	password="root"

kubectl apply -f ../kubernetes/secrets.yaml
kubectl apply -f ../kubernetes/database.yaml
kubectl wait --for=condition=Ready pods -l app=school-database -n student-api --timeout=180s
kubectl apply -f ../kubernetes/application.yaml
