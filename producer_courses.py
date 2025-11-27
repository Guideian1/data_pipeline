import os
import json
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables for (Kafka, Dropbox token, ...,)
load_dotenv()

DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]
KAFKA_TOPIC = "courses"

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
    Process a CSV file from Dropbox and publish each row to Kafka.
    
    Steps:
    - Download CSV text
    - Split into lines
    - Extract header and map each row to header fields
    - Send each record to the 'courses' Kafka topic
    """
    csv_text = download_file(path)
    lines = csv_text.strip().splitlines()

    # First line contains column names
    header = lines[0].split(";")
    
    # Convert each CSV row into a dict and send to Kafka
    for row in lines[1:]:
        values = row.split(";")
        record = dict(zip(header, values))
        producer.send(KAFKA_TOPIC, record)

    # Ensure all messages are delivered before exiting
    producer.flush()
    print(f"[Courses] All records from {path} sent to Kafka")
