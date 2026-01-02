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

## Additional Resources

- [Containerlab Documentation](https://containerlab.dev/)
- [Snappi Documentation](https://github.com/open-traffic-generator/snappi)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Arista cEOS Documentation](https://www.arista.com/en/support/software-download)
- [Git Documentation](https://git-scm.com/doc)
