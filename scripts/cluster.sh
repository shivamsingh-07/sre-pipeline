#!/bin/bash

set -e

PROFILE="sre-pipeline"

cluster_exists() {
	minikube profile list -o json | grep -q "$PROFILE"
}

create_cluster() {
	echo "🚀 Creating 4-node cluster (1 master + 3 workers)..."
	minikube start -p $PROFILE --nodes 4 --memory 2048

	echo "⏳ Waiting for nodes to be ready..."
	kubectl wait --for=condition=Ready nodes --all --timeout=60s

	echo "🏷️ Labeling worker nodes..."
	kubectl label node ${PROFILE}-m02 node-role.kubernetes.io/worker=worker type=application
	kubectl label node ${PROFILE}-m03 node-role.kubernetes.io/worker=worker type=database
	kubectl label node ${PROFILE}-m04 node-role.kubernetes.io/worker=worker type=dependent_services

	echo "📊 Enabling metrics server..."
	minikube addons enable metrics-server -p $PROFILE

	echo "✅ Cluster ready!"
	kubectl get nodes -o wide
}

start_cluster() {
	if cluster_exists; then
		echo "▶️ Starting existing cluster..."
		minikube start -p $PROFILE
	else
		echo "⚠️ Cluster not found. Creating a new one..."
		create_cluster
		return
	fi
}

stop_cluster() {
	if cluster_exists; then
		echo "🛑 Stopping cluster..."
		minikube stop -p $PROFILE
		echo "⏸️ Cluster stopped."
	else
		echo "⚠️ Cluster does not exist."
	fi
}

delete_cluster() {
	if cluster_exists; then
		echo "🔥 Deleting cluster..."
		minikube delete -p $PROFILE
		echo "🗑️ Cluster deleted."
	else
		echo "⚠️ Cluster does not exist."
	fi
}

status_cluster() {
	if cluster_exists; then
		echo "📊 Cluster status:"
		minikube status -p $PROFILE
		kubectl get nodes
	else
		echo "⚠️ Cluster does not exist."
	fi
}

case "$1" in
create)
	create_cluster
	;;
start)
	start_cluster
	;;
stop)
	stop_cluster
	;;
delete)
	delete_cluster
	;;
status)
	status_cluster
	;;
*)
	echo "Usage: $0 {create|start|stop|delete|status}"
	exit 1
	;;
esac
