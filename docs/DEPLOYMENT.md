# Deployment Guide

This document describes how to deploy TaskFlow from scratch on AWS EC2. Existing deployments are updated automatically by the Jenkins pipeline on every push to `main`.

## Prerequisites

- AWS account with EC2 access
- An SSH key pair for the target region (Canada Central / ca-central-1 in this setup)
- GitHub account (for pulling the source repository)
- Local machine with SSH client and a web browser

## Provisioning the EC2 Instance

1. **Launch instance**
   - AMI: Ubuntu Server 24.04 LTS (free-tier eligible)
   - Instance type: `t2.micro`
   - Storage: 20 GB gp3
   - Key pair: create or select an existing `.pem` key
   - Region: ca-central-1

2. **Configure security group** (`taskflow-sg`)
   | Port | Protocol | Source | Purpose |
   |------|----------|--------|---------|
   | 22 | TCP | Your IP | SSH access |
   | 5000 | TCP | 0.0.0.0/0 | Application (public) |
   | 8080 | TCP | Your IP | Jenkins (admin only) |

3. **Save the key pair file** locally and lock down its permissions:
```bash
   mv ~/Downloads/taskflow-key.pem ~/.ssh/taskflow-key.pem
   chmod 400 ~/.ssh/taskflow-key.pem
```

## Initial Server Setup

Connect to the instance:

```bash
ssh -i ~/.ssh/taskflow-key.pem ubuntu@<PUBLIC_IP>
```

Update the system and install Docker:

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

Log out and back in so the group change takes effect.

Configure 2 GB of swap to handle memory pressure:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
```

## Deploying the Application

Clone the repository:

```bash
cd ~
git clone https://github.com/zuhaib31/taskflow.git
cd taskflow
```

Create the production `.env` file (this file is `.gitignore`'d, so it never lives in source control):

```bash
cat > .env << 'ENVEOF'
MYSQL_ROOT_PASSWORD=<strong-root-password>
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=taskflow_user
MYSQL_PASSWORD=<strong-app-password>
MYSQL_DB=taskflow
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=<generate-with-python3-c-import-secrets-print-secrets-token_hex-32>
APP_PORT=5000
ENVEOF
```

Generate a strong `SECRET_KEY`:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Start the application stack:

```bash
docker compose up -d
```

Verify the containers are healthy:

```bash
docker ps
```

The application is accessible at `http://<PUBLIC_IP>:5000`.

## Setting Up Jenkins

Build the custom Jenkins image:

```bash
docker build -t taskflow-jenkins:latest ~/taskflow/jenkins/
```

Identify the host's `docker` group GID (required for Jenkins to access the Docker socket):

```bash
getent group docker
```

Note the number (e.g., `986`).

Create a persistent volume for Jenkins data and run the container:

```bash
docker volume create jenkins_home

docker run -d \
  --name jenkins \
  --restart unless-stopped \
  -p 8080:8080 \
  -p 50000:50000 \
  --group-add <DOCKER_GID> \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/ubuntu/taskflow:/home/ubuntu/taskflow \
  taskflow-jenkins:latest
```

Replace `<DOCKER_GID>` with the number from `getent group docker`.

## Accessing the Jenkins UI

Jenkins is not exposed publicly. Access it via SSH tunnel from your local machine:

```bash
ssh -i ~/.ssh/taskflow-key.pem -L 8080:localhost:8080 ubuntu@<PUBLIC_IP>
```

Leave this terminal open. Then in your browser:
http://localhost:8080
The initial admin password is retrievable inside the Jenkins container:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Complete the setup wizard, install suggested plugins, and create an admin user.

## Configuring the Pipeline Job

In Jenkins:

1. **New Item** → name: `taskflow-pipeline`, type: **Pipeline**
2. Under **Build Triggers**, enable **Poll SCM** with schedule: `H/5 * * * *` (every 5 minutes)
3. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/zuhaib31/taskflow.git`
   - Branches: `*/main`
   - Script Path: `Jenkinsfile`
4. **Save**

Trigger the first build with **Build Now** to verify everything works.

## Updating the Application

Once Jenkins is configured, deployments happen automatically:

1. Push code to the `main` branch on GitHub
2. Within 5 minutes, Jenkins detects the change
3. The pipeline runs: Checkout → Sync → Test → Build → Deploy → Health Check
4. If all stages pass, the new version is live

No manual SSH or commands required after a code push.

## Common Operations

### View application logs
```bash
docker compose logs -f web
```

### View Jenkins logs
```bash
docker logs -f jenkins
```

### Restart the application stack
```bash
cd ~/taskflow && docker compose restart
```

### Pause for cost savings
Stop the EC2 instance from the AWS console. All volume data (Jenkins config, MySQL data) persists. Note that the public IP changes on restart, requiring security group updates for SSH and Jenkins access.

### Resume from pause
1. Start the EC2 instance from AWS console
2. Update the security group's SSH and 8080 rules to your current IP
3. Reconnect via SSH (containers auto-start due to `restart: unless-stopped`)
4. Reopen the Jenkins SSH tunnel if accessing the UI

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| App URL times out | Security group rule for port 5000 not set, or wrong IP | Verify security group, confirm using current public IP |
| Jenkins URL won't load | SSH tunnel dropped or 8080 rule has stale IP | Reopen SSH tunnel, update security group rule |
| `docker exec jenkins docker ps` says permission denied | Docker group GID mismatch | Re-run Jenkins container with correct `--group-add` value |
| Pipeline fails at Health Check | Container takes longer than 60s to be healthy | Check `docker compose logs web` for app startup errors |
| Pipeline fails at Test | A test is genuinely failing | Inspect the pytest output in the console log; fix the failing test before merging |
