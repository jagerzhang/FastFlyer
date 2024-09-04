import os
from fastkit.discovery import Polaris
from fastflyer.utils import get_host_ip, get_log_path, get_env_list

host_ip = get_host_ip()
log_path = get_log_path()
flyer_polaris_enabled = int(os.getenv("flyer_polaris_enabled", 0))
polaris_namespace = os.getenv("flyer_polaris_namespace",
                              os.getenv("POLARIS_NAMESPACE"))
polaris_service_name = os.getenv("flyer_polaris_service",
                                 os.getenv("POLARIS_NAME"))
polaris_service_token = os.getenv("flyer_polaris_token",
                                  os.getenv("POLARIS_TOKEN"))
polaris_heartbeat_interval = int(
    os.getenv("flyer_polaris_heartbeat_interval", 5))
polaris_service_port = int(os.getenv("flyer_port", 8080))
polaris_metadata = get_env_list(prefix="flyer_polaris_metadata_", replace=True)

polaris = Polaris(namespace=polaris_namespace,
                  service=polaris_service_name,
                  service_token=polaris_service_token,
                  host=host_ip,
                  port=polaris_service_port,
                  metadata=polaris_metadata,
                  heartbeat_interval=polaris_heartbeat_interval,
                  misfire_grace_time=10,
                  max_instances=1000,
                  log_path=log_path) if flyer_polaris_enabled == 1 else None
