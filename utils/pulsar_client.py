import pulsar
import os

PULSAR_URL = os.getenv("PULSAR_URL", "pulsar://localhost:6650")
DEFAULT_TOPIC = "persistent://public/default/eventos-nuam"

def publish_event(data, topic=DEFAULT_TOPIC):
    """Envía un mensaje a Pulsar"""
    client = pulsar.Client(PULSAR_URL)
    producer = client.create_producer(topic)
    producer.send(data.encode('utf-8'))
    client.close()
