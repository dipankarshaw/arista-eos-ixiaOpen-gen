# cEOS Lab with Snappi & Streamlit

This lab demonstrates a containerlab setup with Arista cEOS routers and Ixia-c traffic generator, controlled via a Streamlit web interface using the Snappi API.

## Lab Topology

```
ceos1 ----eth1---- ceos2
  |                  |
 eth2              eth2
  |                  |
  +---- ixia-c ------+
       (eth1)   (eth2)
```

## Prerequisites

- Docker
- Containerlab
- Python 3.11+
- Arista cEOS image: `ceosimage:4.35.1F`

## Step 1: Deploy the Containerlab Topology

Start the containerlab topology:

```bash
cd /home/clab/ceos-lab
sudo containerlab deploy -t ceos.clab.yml
```

Verify the deployment:

```bash
sudo containerlab inspect -t ceos.clab.yml
```

Access the nodes:

```bash
# Access ceos1
sudo docker exec -it clab-ceos-ceos1 Cli

# Access ceos2
sudo docker exec -it clab-ceos-ceos2 Cli

# Access ixia-c
sudo docker exec -it clab-ceos-ixia-c sh
```

## Step 2: Set Up Python Virtual Environment

Create and activate the virtual environment:

```bash
cd /home/clab/ceos-lab
python3 -m venv snappi
source snappi/bin/activate
```

## Step 3: Install Required Python Packages

Install snappi and streamlit:

```bash
pip install snappi
pip install streamlit
```

Or install all dependencies at once:

```bash
pip install snappi streamlit
```

## Step 4: Run the Streamlit Application

Start the Streamlit web interface:

```bash
cd /home/clab/ceos-lab/snappi
streamlit run streamlit_app.py
```

The application will start on `http://localhost:8501` by default.

If you need to run it on a specific port or allow external access:

```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## Using the Streamlit Application

### Traffic Page

Configure and send bidirectional traffic flows between ixia-c ports:
- **Eth1 → Eth2**: Configure source/destination MAC, IP, TCP ports, frame size, packet count, and PPS
- **Eth2 → Eth1**: Optional reverse flow with similar parameters
- View traffic metrics after execution

### BGP Page

Configure BGP sessions on both ixia-c interfaces:
- **eth1 Configuration**: Port settings, BGP peer config, and advertised routes
- **eth2 Configuration**: Independent BGP configuration for the second interface
- **Push BGP Config**: Establishes BGP sessions and advertises routes
- **Stop BGP Session**: Gracefully stops all BGP sessions

## Cleanup

To stop and remove the lab:

```bash
cd /home/clab/ceos-lab
sudo containerlab destroy -t ceos.clab.yml
```

To deactivate the virtual environment:

```bash
deactivate
```

## Configuration Files

- `ceos.clab.yml`: Containerlab topology definition
- `ceos1.conf`: Startup configuration for ceos1 router
- `ceos2.conf`: Startup configuration for ceos2 router
- `mymapping.json`: Interface mapping for cEOS
- `snappi/streamlit_app.py`: Streamlit web application

## Troubleshooting

### Virtual Environment Issues

If the virtual environment doesn't activate:
```bash
rm -rf snappi
python3 -m venv snappi
source snappi/bin/activate
```

### Containerlab Connection Issues

Check if containers are running:
```bash
sudo docker ps | grep clab-ceos
```

Restart a specific container:
```bash
sudo docker restart clab-ceos-ixia-c
```

### Streamlit Not Starting

Ensure you're in the correct directory and virtual environment is active:
```bash
cd /home/clab/ceos-lab/snappi
source ../snappi/bin/activate  # if not already activated
streamlit run streamlit_app.py
```

## Sharing Your Lab via Git

### Initialize Git Repository

If not already a Git repository, initialize it:

```bash
cd /home/clab/ceos-lab
git init
```

### Create .gitignore

Create a `.gitignore` file to exclude unnecessary files:

```bash
cat > .gitignore << 'EOF'
# Python virtual environment
snappi/

# Containerlab generated files
clab-ceos/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
EOF
```

### Add and Commit Files

```bash
# Add all relevant files
git add ceos.clab.yml ceos1.conf ceos2.conf mymapping.json README.md
git add snappi/streamlit_app.py

# Commit the changes
git commit -m "Initial commit: cEOS lab with Snappi and Streamlit"
```

### Push to Remote Repository

#### Option 1: GitHub

1. Create a new repository on GitHub (https://github.com/new)
2. Add the remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### Option 2: GitLab

1. Create a new project on GitLab (https://gitlab.com/projects/new)
2. Add the remote and push:

```bash
git remote add origin https://gitlab.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### Option 3: SSH Authentication (Recommended)

If you prefer SSH over HTTPS:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub

# Add the key to GitHub/GitLab settings, then use SSH URL
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Updating the Repository

After making changes:

```bash
# Check status
git status

# Add modified files
git add .

# Commit with a message
git commit -m "Description of changes"

# Push to remote
git push
```

### Cloning the Repository (For Others)

Others can clone your repository with:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

Then follow the setup steps in this README to deploy the lab.

## Additional Resources

- [Containerlab Documentation](https://containerlab.dev/)
- [Snappi Documentation](https://github.com/open-traffic-generator/snappi)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Arista cEOS Documentation](https://www.arista.com/en/support/software-download)
- [Git Documentation](https://git-scm.com/doc)
