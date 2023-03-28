import requests
import json
import os
from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# load_dotenv()
# from linebot.models import TextSendMessage
# from linebot import (
#     LineBotApi, WebhookHandler
# )

line_notify_url = "https://notify-api.line.me/api/notify"
line_notify_token = os.getenv('LINE_NOTIFY_TOKEN')

# class SlackNotification:
#     def __init__(self, context, slack_webhook):
#         self.context = context
#         self.slack_webhook = slack_webhook
#     def push(self):
#         slack_data = {
#             "username": "NotificationBot",
#             "icon_emoji": ":satellite:",
#             "channel" : "#random",
#             "attachments": [
#                 {
#                     "color": "#a633ee",
#                     "fields": [
#                         {
#                             "title": "New Incoming Message :zap:",
#                             "value": self.context,
#                             "short": "false",
#                         }
#                     ]
#                 }
#             ]
#         }
#         headers = {'Content-Type': "application/json"}
#         response = requests.post(self.slack_webhook, data=json.dumps(slack_data), headers=headers)
#         if response.status_code != 200:
#             raise Exception(response.status_code, response.text)

class LineNotification:
    def __init__(self, context, Channel_Access_Token=None, ):
        self.context = context
        # self.line_bot_api = LineBotApi(Channel_Access_Token)
    # def push_line_bot(self, target):
    #     self.line_bot_api.push_message(target, TextSendMessage(text=self.context))

    def push_line_notify(self):
        headers = {
            "Authorization": f"Bearer {line_notify_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {"message": self.context}
        response = requests.post(line_notify_url, headers=headers, data=payload)

        # response = requests.post(line_notify_url, headers=headers, data=payload)
        print(response)
class WebCrawlerUSA:
    def __init__(self):
        self.rs = requests.session()
        self.urls = [
            ('道瓊指數','https://invest.cnyes.com/index/GI/DJI'), # DJI
            ('S&P 500','https://invest.cnyes.com/index/GI/INX'), # SPX
            ('費城半導體','https://invest.cnyes.com/index/GI/SOX'),# 費城半導體
            ('那斯達克綜合指數','https://invest.cnyes.com/index/GI/IXIC'),# NASDAQ
        ]
        self.result = []

    def fetch(self):
        for url in self.urls:
            res = self.rs.get(url[1], verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')
            info_date = soup.select('._zFXfK')[0].text
            info_date = info_date.split(' ')[0]
            info_price = soup.select('.jsx-2214436525.info-price')[0].text
            info_net = soup.select('.jsx-2214436525.change-net')[0].text
            info_percent = soup.select('.jsx-2214436525.change-percent')[0].text
            if '+' in info_net:
                info = '{}▲  {}▲'.format(info_net, info_percent)
                info = info.replace('+', '')
            else:
                info = '{}▼  {}▼'.format(info_net, info_percent)
                info = info.replace('-', '')
            self.result.append('{}-{}\n{}\n{}'.format(info_date, url[0], info_price, info))

    def push(self, slack_webhook=None, line_token=None):
        result = '\n'+'\n\n'.join(self.result)
        try:
            msg = LineNotification(result)
            msg.push_line_notify()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    crawler = WebCrawlerUSA()
    crawler.fetch()
    crawler.push()

    # crawler.push(os.getenv('SLACK_WEBHOOK'), os.getenv('CHANNEL_ACCESS_TOKEN'))