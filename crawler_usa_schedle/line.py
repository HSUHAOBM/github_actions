import requests
import os
from dotenv import load_dotenv
load_dotenv()

url = "https://notify-api.line.me/api/notify"
token = os.getenv('LINE_NOTIFY_TOKEN')
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/x-www-form-urlencoded"
}
payload = {"message": "Hello, world!"}
response = requests.post(url, headers=headers, data=payload)
print(response.status_code)