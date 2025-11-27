import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
app = Flask(__name__)

# File used to store the Dropbox cursor for tracking changes
CURSOR_FILE = "dropbox_cursor.txt"

# Import producer functions for different folders
from producer_universities import process_file as process_universities
from producer_courses import process_file as process_courses

# Dropbox API token from environment variable
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]


def get_cursor():
    """
    Reads and returns the saved Dropbox cursor value.
    This cursor lets us fetch only new changes instead of scanning all files.
    """
    return open(CURSOR_FILE).read().strip() if os.path.exists(CURSOR_FILE) else None


def save_cursor(cursor):
    """
    Saves the latest Dropbox cursor value to local storage.
    """
    with open(CURSOR_FILE, "w") as f:
        f.write(cursor)


def list_folder_changes(cursor):
    """
    Calls Dropbox /list_folder/continue to get new file changes since the last cursor.
    """
    url = "https://api.dropboxapi.com/2/files/list_folder/continue"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/json"
    }

    # Request Dropbox for the next batch of changes
    r = requests.post(url, headers=headers, json={"cursor": cursor})
    r.raise_for_status()
    return r.json()


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """
    Handles Dropbox webhook events.
    - GET: Dropbox challenge verification
    - POST: Triggered when a file changes in Dropbox
    """
    # Dropbox webhook verification
    if request.method == "GET":
        return request.args.get("challenge", ""), 200

    # Handle file change notifications
    cursor = get_cursor()
    if cursor:
        changes = list_folder_changes(cursor)
        save_cursor(changes["cursor"])

        # Loop through changed entries (files created/updated)
        for entry in changes.get("entries", []):
            if entry[".tag"] != "file":
                continue  # Ignore folders or deletions

            path = entry["path_lower"]
            print("File changed:", path)

            # Route to correct producer based on folder
            if path.startswith("/universities/"):
                process_universities(path)
            elif path.startswith("/courses/"):
                process_courses(path)

    return "", 200


if __name__ == "__main__":
    # If no cursor exists, initialize it by scanning the Dropbox root folder
    if not get_cursor():
        r = requests.post(
            "https://api.dropboxapi.com/2/files/list_folder",
            headers={
                "Authorization": f"Bearer {DROPBOX_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"path": "", "recursive": True}
        )
        save_cursor(r.json()["cursor"])

    # Start Flask server
    app.run(port=5000)
