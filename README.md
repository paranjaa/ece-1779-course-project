# Ticker (ece-1779-course-project)
Course project for Fall 2025 ECE 1779 (Intro to Cloud Computing) Course

## Team Information
|                | David Zhang                    | Alok Paranjape                  |
|:---------------|:-------------------------------|:--------------------------------|
| E-mail         | davidcw.zhang@mail.utoronto.ca | alok.paranjape@mail.utoronto.ca |
| Student Number | 1003260918                     | 1008782364                      |

## Motivation
Across multiple commercial sectors, such as retail or logistics, there’s a distinct need for accurate and timely inventory management. Traditional paper-based management systems, and existing software solutions may be unable to provide detailed and up to the minute recordkeeping, which may be taxing on operational efficiency and profits. Additionally, analyzing and reporting statistics generally require a lot of manual labour when using traditional solutions. With this project, we intend to make a software solution that automatically handles inventory management, in a way that improves upon these qualities by using cloud computing. 

Due to the ubiquity of inventory management, there are a plethora of possible users of this system. For example, B2B companies such as Salesforce or B2C companies such as local grocery stores or restaurants, handle and move large amounts of inventory across the world. The volume of such transactions necessitates automated management of inventory and the diverse distribution of such logistics networks requires cloud computing with localized edge nodes to minimize latency and maximize data accessibility. Due to the top down nature of inventory management, while the customer base might include different companies and industries, the user base would include different levels of employees, such as managers and staff members.

Existing solutions, such as traditional paper management or accounting software solutions (such as Clover or Square) cannot keep up with the volume of transactions. Additionally, the management of inventory in real-time is infeasible when most of the work is still done by human operators. Market and inventory trend reports are used to properly direct the financial decisions within a company. Without these reports, the company may need to compensate with unnecessarily large stock buffers to avoid understocking. However, these reports are unattainable in real-time using traditional implementations. Thus, an automated, distributed, inventory management system is required. Such a system can set up inventory threshold mechanisms to automatically handle any deviations from set targets for every item. This system can also generate reports of the entire inventory on-demand. As such, the project could offer some substantial improvements over existing solutions.

## Objective
This project is a technical showcase of how an inventory management service can be quickly deployed to a cloud provider, and scaled to ensure that the service is always available. Additionally, this project also shows the ease of use of manipulating inventory data in real time that can be accessed from anywhere at anytime (as long as the user is authorized and authenticated). This should show a clear improvement over the use of physical mediums, such as paper invoices, to keep track of inventory.

## Technical Stack
| Requirement         | Approach                                                                                                                                  |
|:--------------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| Containerization    | Docker for containerizing the Python backend services and `docker compose` for local development                                          |
| State Management    | PostgreSQL for relational data storage and DigitalOcean Volumes for state persistence                                                     |
| Deployment Provider | DigitalOcean                                                                                                                              |
| Orchestration       | Docker Swarm for service replication and load balancing                                                                                   |
| Secret Management   | Docker Secrets                                                                                                                            |
| Monitoring          | DigitalOcean Metrics enabled on droplets for CPU/RAM/Network usage and Prometheus + Grafana to monitor Python backend request throughputs |

## Features
This project follows Example Project \#4 as a guideline.

* The system as a whole will be hosted on [DigitalOcean](https://www.digitalocean.com/) to ensure high availability and low latency across multiple data regions. To promote rapid application development, we will develop the backend primarily with Python and then containerize it using Docker. These will then be orchestrated with Docker Swarm to allow for replication and scaling of each service independently.

* To support the inventory management system we will use PostGreSQL to robustly store the data. CRUD operations will be used to manage the inventory system by, respectively, adding/displaying/modifying/removing items from the system. 

* In order to be accessible, all of these operations will be actionable from a user-readable dashboard that queries through the Python backend and displays the inventory and permitted actions legibly. This dashboard will also allow for fine-tuned searching and filtering of inventory by user-defined qualifiers. 

* Most notably, we will also have role-based access such that these operations will only be permitted should the user be assigned the appropriate role. This will include additional security enhancements, for authenticating and authorizing users. We will also periodically trigger automated backups of the database to ensure resiliency against data loss. 

* Finally, we will also have integrations that trigger outside of the dashboard, such as certain conditions being met (e.g. the quantity of an inventory item exceeding a set range) to send email notifications to the appropriate people, and real time stock updates.

To reiterate, this implementation fulfills the basic features required for the ECE1779 course project and implements auto-scaling of internal services, integration with external services, and handling authentication/authorization and secret management as advanced features.

## User Guide
You can access the live service at http://147.182.153.38:5000. Credentials sent to the TA.

Simply login to the service and you will be presented with the inventory display. 

* As any logged-in user, you can increment or decrement any item, or sort the inventory using several parameters with the appropriate buttons.

* As any user with a manager role or better, you can add or remove item listings using the entry box and the delete button respectively.

* As an administrator role, you can enroll other users as regular users or manager users through the endpoint http://147.182.153.38:5000/enroll (or by clicking the link in the inventory page). Doing this will add a new user with the designated username, (hashed) password, and role to the database and allow them to log in to the same system.

For analyzing the Python backend metrics, log in to the Grafana endpoint http://138.197.145.187:3000 and observe the dashboard provided.

## Development Guide
### Running this locally using Docker Compose
<b>Known Issue: </b>When running this locally, Prometheus and Grafana are both deployed successfully, however, Grafana is unable to access the Prometheus api endpoints.
1. Set up a `.env` file with the following secrets filled:
```text
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=
```
2. Run `docker compose up` to start the dockerized application and the database locally.
3. Run `docker compose down --volumes` to stop the dockerized application and the database locally.

### Running this on DigitalOcean using Docker Swarm

#### Prerequisites:
1. Ensure that you have built the docker image of the python backend `./app` and pushed it to a Docker image repository.
```shell
cd ./app
docker build -t ece1779-project-app .
docker tag ece1779-project-app <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
docker push <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
```
2. [Create an access token](https://docs.docker.com/security/access-tokens/) (read only) that can access the repository you have pushed it to.
3. Edit `stack_prod.yaml` to point to the Docker image hosted in the repository
```yaml
services:
  app:
    image: <YOUR_GIT_USERNAME><YOUR_PRIVATE_REPOSITORY>:ece1779-project-app
```

#### DigitalOcean Setup:
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
4. SSH into each droplet and [install docker engine](https://docs.docker.com/engine/install/ubuntu/) on all of them. <b>Execute each block separately.</b>
```shell
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
```
```shell
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
```shell
# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```
```shell
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
8. Securely copy `./prometheus/prometheus.yml` to the manager node.
```shell
scp ./prometheus/prometheus.yml root@<MANAGER_NODE_DROPLET>:/root/prometheus/
```
9. Create a `.secrets` directory in the manager node's content root.
```shell
mkdir ~/.secrets 
```
10. Create four secrets files `.secrets/.app_secret_key.txt`, `.secrets/.db_name.txt`, `.secrets/.db_password.txt`, `.secrets/.db_user.txt` and populate them with the appropriate secrets. An example is shown below. <b>WARNING: Ensure that you do not have any trailing whitespace, carriage return, or newline characters in the contents of these secrets.</b>

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
11. Still on the manager node, flag the Docker Swarm node that has the attached volume.
```shell
docker node update --label-add volume=true <DROPLET_NAME>
```
12. Login to Docker on the manager node using the secure access token with read access that you set up earlier. It will ask for a Personal Access Token. Paste it in after it asks for one.
```shell
docker login -username <DOCKER_USERNAME>
```
13. Run the application through Docker Swarm
```shell
docker stack deploy -c ./stack_prod.yaml ece1779-project --with-registry-auth
```

#### Diagnosing Issues:
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

#### Teardown the service
```shell
docker stack rm ece1779-project
```

### Testing the service
You can test out the service by simply going to the appropriate ip address on any browser (`127.0.0.1:5000/` if running locally or `<droplet_ipv4>:5000/` if running on DigitalOcean).  

This will automatically redirect you to the login endpoint `/login`.  

After logging in, you may perform CRUD actions (Create and Delete only if your user role permits it) or add new users with a specific role (with the admin role only).

```text
/
/login
/enroll
/logout
```

You can access Prometheus metrics via the manager node `<manager_droplet_ipv4>:9090`.

You can additionally access the Grafana dashboards by accessing the node it is running on `<droplet_ipv4>:3000`. Because of the way these services are load balanced by Docker Swarm, it is highly likely that Grafana is running on the non-manager node.

## Deployment Information
The live service can be accessed at http://147.182.153.38:5000

The Grafana dashboard can be accessed at http://138.197.145.187:3000

## Individual Contributions
| David Zhang                                                                               | Alok Paranjape     |
|:------------------------------------------------------------------------------------------|:-------------------|
| Set up the Python backend service                                                         | <insert work here> |
| Added authentication and authorization to the Python backend application                  |                    |
| Dockerized the Python backend service and set up local development with `docker compose`  |                    |
| Set up PostgreSQL, Prometheus, and Grafana                                                |                    |
| Set up the orchestration using Docker Swarm (with replicas) `docker stack`                |                    |
| Provisioned several DigitalOcean droplets and deployed this service to those droplets     |                    |
| Documented the steps needed to deploy this application to DigitalOcean                    |                    |
| Wrote this README.md file                                                                 |                    | 

## Lessons Learned and Concluding Remarks
This project has given us a lot more appreciation of the tools already set in place for other workflows (e.g. in companies). It was difficult to judge how much work and how the work could be allocated before the service was deployed. Simultaneously, the service could not be deployed without already finishing the required features (Dockerized Python backend, PostgreSQL + mounted volume, Docker Swarm config, Docker Secrets management, DigitalOcean Droplet and Volume provisioning). We ended up needing to wait on each other to finish their parts before the next step could be done. However, once the entire service was deployed successfully, development could easily happen in parallel, especially because we could build our own versions of the `app.py` Docker image and deploy it locally for testing. Finally, it was surprisingly easy to add other microservices to the Docker stack config (although we did run into some memory and CPU limits at that time with our Droplets). 

We also encountered several issues during development due to different system architectures. For example, our development was split across Windows, MacOS, and Linux which led to several inconsistencies when sharing bash  setup scripts with each other. Additionally, the MacOS environment was running on an Apple Silicon chip which uses ARM architecture while all other environments were using x86. This restricted local development heavily with our original plan of using Kubernetes (which does not work on Windows 11 Home version) deploying Dockerized applications (which were built on x86 and could not run on ARM architectures). Thus, we ended up pivoting to using Docker Swarm instead to mitigate one of these issues. 

Overall, this project was an interesting preview into the software development cycle of cloud computing and web applications.