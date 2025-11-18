# ece-1779-course-project
Course project for Fall 2025 ECE 1779 (Intro to Cloud Computing) Course

## Running this locally using Docker Compose 
Run `docker compose up` to start the dockerized application and the database locally.

Run `docker compose down --volumes` to stop the dockerized application and the database locally.

## Running this on DigitalOcean using Docker Swarm

### Prerequisites:
1. Ensure that you have built the docker image of the python backend `./app` and pushed it to a Docker image repository.
```shell
cd ./app
docker build -t ece1779-project-app .
docker tag ece1779-project-app <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
docker push <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
sleep 20
```
2. [Create an access token](https://docs.docker.com/security/access-tokens/) (read only) that can access the repository you have pushed it to.
3. Edit `stack_prod.yaml` to point to the Docker image hosted in the repository
```yaml
services:
  app:
    image: <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
```

### DigitalOcean Setup:
1. Create as many DigitalOcean droplets as you want (for this example, 2 droplets). <b>Keep track of the droplet ipv4 addresses and the droplet names.</b>
```text
region: Toronto
OS: Ubuntu
Version: 24.04 (LTS) x64
Droplet Type: Basic
CPU options: Regular
    512 MB RAM
    10 GB SSD
    500 GB Transfer
Hostname: name_of_droplet
```
or alternatively
```shell
curl -X POST -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer '$TOKEN'' \
    -d '{"name":"name_of_droplet",
        "size":"s-1vcpu-512mb-10gb",
        "region":"tor1",
        "image":"ubuntu-24-04-x64",
        "monitoring":true,
        "vpc_uuid": <your_vpc_uuid> }' \
    "https://api.digitalocean.com/v2/droplets"
```
2. Create a DigitalOcean volume (Volume Block Storage) and attach it to one of the droplets. <b>Keep track of the volume name and which droplet it was attached to.</b>
```text
Volume Size: 1GB
Filesystem: Ext4
Volume Name: name_of_volume
```
3. Edit `stack_prod.yaml` to point the database to your mounted volume. <b>WARNING: File paths use underscores, not dashes. A volume named `volume-tor1-01` needs to be referenced as `volume_tor1_01` in the `stack_prod.yaml` file.</b>
```yaml
  db:
    image: postgres:latest
    deploy:
      ...
    ports:
      ...
    environment:
      ...
    volumes:
      - /mnt/<NAME_OF_VOLUME>:/var/lib/postgresql
```
4. SSH into each droplet and [install docker engine](https://docs.docker.com/engine/install/ubuntu/) on all of them.
```shell
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update 
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
5. Pick one of the droplets to be the Docker Swarm manager node. Initialise a Docker Swarm from inside that droplet's shell using that droplet's ip address. <b>Copy the command that is outputted for joining the Swarm on other nodes.</b>
```shell
docker swarm init --advertise-addr <MANAGER_NODE_DROPLET_IPv4>
```
6. Join the Docker Swarm as worker nodes on <u>all other droplets</u> using the command copied from the previous step. 
```shell
docker swarm join --token <TOKEN> <MANAGER_NODE_DROPLET_IPv4>:<MANAGER_NODE_PORT>
```
7. Securely copy `stack_prod.yaml` and `init.sql` to the manager node.
```bash
scp ./stack_prod.yaml root@<MANAGER_NODE_DROPLET_IPv4>:/root/
scp ./init.sql root@<MANAGER_NODE_DROPLET_IPv4>:/root/
```
8. Create a `.secrets` directory in the manager node's content root.
```shell
mkdir ~/.secrets 
```
9. Create four secrets files `.secrets/.app_secret_key.txt`, `.secrets/.db_name.txt`, `.secrets/.db_password.txt`, `.secrets/.db_user.txt` and populate them with the appropriate secrets. An example is shown below. <b>WARNING: Ensure that you do not have any trailing whitespace, carriage return, or newline characters in the contents of these secrets.</b>

`.app_secret_key.txt`
```text
ece1779
```
`.db_name.txt`
```text
inventorydb
```
`.db_password.txt`
```text
password
```
`.db_user.txt`
```text
user
```
10. Still on the manager node, flag the Docker Swarm node that has the attached volume.
```shell
docker node update --label-add volume=true <DROPLET_NAME>
```
11. Login to Docker on the manager node using the secure access token with read access that you set up earlier. It will ask for a Personal Access Token. Paste it in after it asks for one.
```shell
docker login -username <DOCKER_USERNAME>
```
12. Run the application through Docker Swarm
```shell
docker stack deploy -c ./stack_prod.yaml ece1779-project --with-registry-auth
```

### Diagnosing Issues:
1. Check the status of the containers
```shell
docker ps
```
2. Check the status of each service (and replicas) separately
```shell
docker service ps ece1779-project_app --no-trunc
docker service ps ece1779-project_db --no-trunc
```
3. Scale up and down the Python service
```shell
docker service scale ece1779-project_app=5
docker service scale ece1779-project_app=1
```

### Teardown the service
```shell
docker stack rm ece1779-project
```

## Testing the service
You can test out the service by simply going to the appropriate ip address on any browser (`127.0.0.1:5000/` if running locally or `<droplet_ipv4>:5000/` if running on DigitalOcean).  

This will automatically redirect you to the login endpoint `/login`.  

After logging in, you may perform CRUD actions (Create and Delete only if your user role permits it) or add new users with a specific role (with the admin role only).

```text
/
/login
/enroll
/logout
```