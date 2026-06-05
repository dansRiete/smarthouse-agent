import requests
import json
from langchain.tools import tool

NODE_RED_URL = "http://nodered:1880/flows"

@tool
def read_node_red_flows(query: str = "") -> str:
    """Useful to read all the current Node-RED workflows and automations. Returns JSON string of all flows."""
    try:
        response = requests.get(NODE_RED_URL, headers={"Accept": "application/json"}, timeout=10)
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return f"Error reading flows: {str(e)}"

@tool
def deploy_node_red_flows(flows_json: str) -> str:
    """Useful to deploy a completely new set of flows to Node-RED. You must provide the FULL JSON array of flows, not just the modified ones. It replaces everything."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Node-RED-Deployment-Type": "full"
        }
        response = requests.post(NODE_RED_URL, headers=headers, data=flows_json, timeout=10)
        response.raise_for_status()
        return "Successfully deployed new Node-RED flows."
    except Exception as e:
        return f"Error deploying flows: {str(e)}"
