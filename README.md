# URL Shortener

A containerized URL shortener service built with FastAPI and PostgreSQL.

## Features

- Shorten long URLs to easy-to-share short links
- Persistent storage with PostgreSQL
- Containerized with Docker
- Kubernetes manifests for production deployment
- Secure configuration using Secrets and ConfigMaps

## Local Development

### Prerequisites

- Docker and Docker Compose

### Running Locally Steps

1. Clone this repository

   ```bash
   git clone https://github.com/sujan-2866/Load-Balanced-URL-Shortener.git
   cd Load-Balanced-URL-Shortener
   ```

2. `docker build -t docker_username/url-shortener:latest .`

3. `docker push docker_username/url-shortener:latest`

4. `minikube start`

5. ```
   kubectl apply -f k8s/app/url-shortener-deployment.yaml
   kubectl apply -f k8s/app/url-shortener-service.yaml
   kubectl apply -f k8s/app/hpa.yaml
   kubectl apply -f k8s/db/postgres-deployment.yaml
   kubectl apply -f k8s/db/postgres-service.yaml
   kubectl apply -f k8s/db/postgres-pvc.yaml
   kubectl apply -f k8s/config/configmap.yaml
   kubectl apply -f k8s/config/secret.yaml
   ```
6. Run the following in a new terminal and keep it running
   `minikube tunnel`

7. Make Sure all the pods are running:
   `kubectl get pods`

8. Get the <EXTERNAL-IP> using the following command:
   `kubectl get svc url-shortener-service`
   Note: We will get the ip only after running `minikube tunnel` in another terminal, otherwise it will say <pending>

### Testing the project

#### Using CURL

- To See all the urls stored in the DB:
  `curl -X GET "http://<EXTERNAL-IP>/urls/"`

- To get a shorten url to website:
  `curl -X POST "http://<EXTERNAL-IP>/shorten/" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'`
  Note: Replace the "<EXTERNAL-IP>" with the <EXTERNAL-IP> we got before.

- To delete a url:
  `curl -X GET "http://<EXTERNAL-IP>/delete/<ShortCode>`

#### Using Frontend

- Run the following in a terminal window and don't terminate:
  `minikube service url-shortener-service --url`

- Access the URL mentioned in the terminal after running the previous command and perform the required operations
