
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests

# LineBot
line_bot_token = ""
line_user_id = ""


# LineBot
class LineBot:
    def __init__(self, context):
        self.context = context
        self.line_bot_api = LineBotApi(line_bot_token)
        self.user_id = line_user_id

    def push_message(self):
        if not self.user_id or not self.line_bot_api:
            raise Exception("LINE Bot token or user ID is missing.")
        try:
            self.line_bot_api.push_message(
                self.user_id,
                TextSendMessage(text=self.context)
            )
            print("Message sent successfully via LINE Bot.")
        except Exception as e:
            print(f"Failed to send message via LINE Bot: {e}")


line_bot = LineBot("TEST")
line_bot.push_message()
