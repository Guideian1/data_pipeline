# **Data Pipeline**
This project implements an automated data ingestion pipeline using Dropbox, Webhooks, Kafka, and Firebase Firestore.
It monitors file changes in Dropbox, processes CSV files, sends records to Kafka topics, and stores them in Firestore.

## System Overview

**The pipeline performs the following tasks:**

1. Dropbox Webhook detects when a file inside the `universities/` or `courses/` folder is added or updated.
2. The webhook triggers the correct Producer, based on file path:
   - `producer_universities.py`
   - `producer_courses.py`
3. Each producer:
   - Downloads the updated CSV file from Dropbox
   - Parses the file
   - Sends each row as a message to Kafka
4. The Kafka Consumer listens to the `universities` and `courses` topics
5. Incoming messages are stored in Firebase Firestore

## Project Structure
/project

│── webhook.py

│── producer_universities.py

│── producer_courses.py

│── consumer.py

│── dropbox_cursor.txt

│── .env

│── requirements.txt

│── .gitignore

│── README.md

## Technologies Used
| Component              | Purpose                                        |
| ---------------------- | ---------------------------------------------- |
| **Flask**              | Exposes the webhook endpoint                   |
| **Dropbox API**        | Detects and downloads files                    |
| **Kafka**              | Message streaming between producers & consumer |
| **Firebase Firestore** | Stores final processed documents               |
| **Python**             | Main programming language                      |
| **dotenv**             | Environment variable management                |

## Data Flow (High-Level Architecture)
`Dropbox > Webhook > Producer > Kafka > Consumer > Firestore`
- Files placed inside Dropbox trigger the system automatically
- Only changed files are processed (cursor-based update tracking)

## How to Run the Pipeline
1. Clone the Repository
2. Create & Fill The .env File
Example:
  ```
  DROPBOX_TOKEN=your_dropbox_token
  KAFKA_BOOTSTRAP=localhost:9092
  FIREBASE_KEY_JSON="type": "...", "project_id": "..."
  ```
  
## Install Dependencies
`pip install -r requirements.txt`

## Running Kafka Using Redpanda (Docker)
Download Docker Desktop
```
docker run -d --pull=always --name=redpanda \
  -p 9092:9092 -p 9644:9644 \
  redpandadata/redpanda:latest \
  redpanda start --overprovisioned --smp 1 --memory 1G \
  --reserve-memory 0M --node-id 0 --check=false
```
## Check if Redpanda is running:
`docker ps`

## Setting Up ngrok for Dropbox Webhooks
You must expose your local webhook to the public internet.
1. Install ngrok from https://ngrok.com
2. Start your webhook server:
  - `python webhook.py`
3. Start ngrok tunnel:
- `ngrok http 5000`
4. Copy the public URL, e.g.:
  `https://abc123.ngrok.io/webhook`
5. Paste it into your Dropbox App Webhook URL settings.
- Now Dropbox can notify your webhook when files change.

## Running the Pipeline
Open 3 terminals:

Terminal 1 — Run webhook:
- `python webhook.py`

Terminal 2 — Run ngrok
- `ngrok http 5000`

Terminal 3 — Run Kafka consumer
- `python consumer.py`

## Testing the Pipeline
1. Upload a CSV file into Dropbox under:
- `/universities/yourfile.csv`
- `/courses/yourfile.csv`
2. Dropbox triggers the webhook
3. Producer sends messages to Kafka
4. Consumer inserts them into Firestore
5. Check Firestore > collections:
  - `universities`
  - `courses`
