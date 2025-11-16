minikube start

minikube image rm inventory-manager-k8s
docker rmi $(docker images --filter=reference="inventory-manager-k8s" -q)

docker build -t inventory-manager-k8s .
minikube image load inventory-manager-k8s

kubectl apply -f api_secret.yaml
kubectl apply -f database_secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

sleep 20

minikube service inventory-manager-service --url
