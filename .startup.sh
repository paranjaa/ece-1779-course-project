minikube start

kubectl apply -f api_secret.yaml
kubectl apply -f database_secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

sleep 20

minikube service inventory-manager-service --url
