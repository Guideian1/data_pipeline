import os
import json
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables for (Kafka, Dropbox token, ...,)
load_dotenv()

DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]
KAFKA_TOPIC = "universities"

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers=[os.environ["KAFKA_BOOTSTRAP"]],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def download_file(path):
    """
    Download a file from Dropbox using the /files/download endpoint.
    
    Args:
        path (str): Dropbox file path (e.g., '/universities/university.csv')
    
    Returns:
        str: File content as plain text (CSV format)
    """
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Dropbox-API-Arg": json.dumps({"path": path})
    }

    # Request the file content directly from Dropbox API
    r = requests.post("https://content.dropboxapi.com/2/files/download", headers=headers)
    r.raise_for_status()
    return r.text


def process_file(path):
    """
    Processes a CSV file from Dropbox and sends each row to Kafka.
    
    Steps:
    - Download file content
    - Split into lines
    - Convert CSV using header row
    - Send each row as a JSON record to Kafka topic
    """
    csv_text = download_file(path)
    lines = csv_text.strip().splitlines()

    # First row contains column names
    header = lines[0].split(";")
    
    # Iterate through all data rows
    for row in lines[1:]:
        values = row.split(";")
        record = dict(zip(header, values))  # Map header to row values
        producer.send(KAFKA_TOPIC, record)

    # Ensure all messages are delivered
    producer.flush()
    print(f"[Universities] All records from {path} sent to Kafka")
