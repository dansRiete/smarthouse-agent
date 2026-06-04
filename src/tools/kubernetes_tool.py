from kubernetes import client, config
from langchain.tools import tool

# Attempt to load in-cluster config, fallback to local config for testing
try:
    config.load_incluster_config()
except:
    try:
        config.load_kube_config()
    except:
        pass

@tool
def get_pod_status(namespace: str = "smarthouse") -> str:
    """Useful to check the status of all pods in a Kubernetes namespace."""
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace)
        res = []
        for p in pods.items:
            res.append(f"Pod: {p.metadata.name}, Status: {p.status.phase}")
        return "\n".join(res)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def restart_deployment(deployment_name: str, namespace: str = "smarthouse") -> str:
    """Useful to restart a kubernetes deployment (equivalent to kubectl rollout restart)."""
    import datetime
    try:
        apps_v1 = client.AppsV1Api()
        now = datetime.datetime.utcnow().isoformat("T") + "Z"
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        apps_v1.patch_namespaced_deployment(deployment_name, namespace, body)
        return f"Successfully restarted deployment {deployment_name} in namespace {namespace}"
    except Exception as e:
        return f"Error restarting deployment: {str(e)}"
