import paho.mqtt.publish as publish
from langchain.tools import tool

@tool
def publish_mqtt_message(topic: str, payload: str) -> str:
    """Useful to control devices by publishing MQTT messages. For example, to control the AC or FAN, publish to 'mqtt.smarthouse.power.control' with payload '{"device": "AC", "state": "off"}'. To control Zigbee devices (like LED_OVER_BED), publish to 'zigbee2mqtt/DEVICE_NAME/set' with payload '{"state": "off", "brightness": 255}'."""
    try:
        publish.single(topic, payload=payload, hostname="smarthouse-mqtt-broker", port=1883, client_id="smarthouse-agent", keepalive=60)
        return f"Successfully published message to {topic}."
    except Exception as e:
        return f"Error publishing MQTT message: {str(e)}"
