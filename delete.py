from solardatatools.dataio import load_cassandra_data
from solardatatools import DataHandler
from statistical_clear_sky import SCSF
from dask.distributed import Client, SSHCluster
import dask

ec2_ips = ["172.31.26.35", "172.31.28.129"]
password="slacgismo"
pem = "~/.pem/dask-ssh-ed25519.pem"

cluster = SSHCluster(
    ec2_ips,
    connect_options={"known_hosts": None, "client_host_keys": pem},
    worker_options={"nthreads": 2, "memory_limit":'15GiB'}
)
client = Client(cluster, processes=False)

@dask.delayed
def pull_and_run(site_id):
    df = load_cassandra_data(site_id, cluster_ip="54.176.95.208")
    dh = DataHandler(df, convert_to_ts=True)
    dh.run_pipeline(power_col='ac_power_01')
    return dh.report(return_values=True)

results = []
site_ids = ["TAAJ01021775", "001C4B0008A5", "TABG01081601"]
for si in site_ids:
    results.append(pull_and_run(si))
dask.compute(results)