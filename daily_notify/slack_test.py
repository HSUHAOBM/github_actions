import requests
import json

# Slack Webhook URL（請替換為你的 Webhook URL）
slack_webhook = ""

# 要發送的訊息內容
message = {
    'username': 'NotificationBot',
    'icon_emoji': ':panda_face:',
    'text': 'Hello, Slack! This is a message from Python.'
}

# 發送 POST 請求到 Slack Webhook
response = requests.post(
    slack_webhook,
    data=json.dumps(message),
    headers={'Content-Type': 'application/json'}
)

# 檢查回應狀態
if response.status_code == 200:
    print('訊息發送成功')
else:
    print(f'發送失敗，狀態碼: {response.status_code}')
    print(f'錯誤訊息: {response.text}')
