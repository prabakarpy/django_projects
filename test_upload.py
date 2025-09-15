import requests
import os

# Define the new, correct API endpoint
API_URL = "http://localhost:8000/api/w2/upload/"
FILE_NAME = "sample_w2.pdf"
FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

print("Attempting to upload the file...")
print(f"filepath---?{FILE_PATH}")
if not os.path.exists(FILE_PATH):
    print(f"Error: The file '{FILE_NAME}' was not found at {FILE_PATH}")
else:
    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': (FILE_NAME, f, 'application/pdf')}
            response = requests.post(API_URL, files=files)

        print("\n--- Response ---")
        print(f"Status Code: {response.status_code}")

        # Check for success (201 Created)
        if response.status_code == 201:
            print("Success! File uploaded and a report ID was created.")
            print(f"Report ID: {response.json().get('report_id')}")
        else:
            print(f"Error: Unexpected status code. Response text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
