import os, json
from kafka import KafkaConsumer
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase Setup
# Load Firebase service account JSON from environment variable
cred = credentials.Certificate(json.loads(os.environ['FIREBASE_KEY_JSON']))

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred)

# Create Firestore client for writing records
db = firestore.client()

# Kafka Consumer Setup
# Subscribe to both topics: universities, courses
consumer = KafkaConsumer(
    "universities",
    "courses",
    bootstrap_servers=[os.environ['KAFKA_BOOTSTRAP']],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),  # decode JSON messages
    auto_offset_reset='earliest'  # read messages from the beginning if no offset exists
)

print("Listening for messages on topics: universities, courses ...")

# Main Listening Loop
# Continuously consume messages as they arrive
for msg in consumer:
    record = msg.value        # Message payload (deserialized JSON)
    topic = msg.topic         # Topic name where the message came from

    print(f"Received from Kafka ({topic}): {record}")

    # Store the data in Firestore depending on topic
    if topic == "universities":
        # Save university information into Firestore collection
        db.collection("universities").document(record["name"]).set(record)
        print(f"Saved university: {record.get('name')}")

    elif topic == "courses":
        # Save course information into Firestore collection
        db.collection("courses").document(record["name"]).set(record)
        print(f"Saved course: {record.get('name')}")
    