import requests
import json
import os
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime


# Slack
slack_webhook = os.getenv('SLACK_WEBHOOK')
# LineBot
line_bot_token = os.getenv('LINE_BOT_TOKEN')
line_user_id = os.getenv('LINE_USER_ID')
# 氣象署 API
cwa_api_key = os.getenv('CWA_API_KEY')


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


# Slack
class SlackNotification:
    def __init__(self, context):
        self.context = context
        self.slack_webhook = slack_webhook

    def push(self):
        slack_data = {
            "username": "美股追蹤",
            'icon_emoji': ':panda_face:',
            "channel": "#測試",
            "attachments": [
                {
                    "color": "#a633ee",
                    "fields": [
                        {
                            "title": "New Incoming Message :zap:",
                            "value": self.context,
                            "short": "false",
                        }
                    ]
                }
            ]
        }
        headers = {'Content-Type': "application/json"}
        response = requests.post(
            self.slack_webhook, data=json.dumps(slack_data), headers=headers)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)


# 氣象資訊
class WeatherForecast:
    def __init__(self, location='高雄市'):
        self.location = location
        self.api_url = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001'
        self.result = ''

    def get_period_name(self, start_time):
        """根據時間判斷時段並加上 emoji"""
        hour = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").hour
        if 5 <= hour < 12:
            return "🌅 早上"
        elif 12 <= hour < 18:
            return "☀️ 白天"
        elif 18 <= hour < 24:
            return "🌃 晚上"
        else:
            return "🌙 凌晨"

    def fetch(self):
        """取得天氣預報資料"""
        params = {
            'Authorization': cwa_api_key,
            'locationName': self.location
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()

            location_data = data['records']['location'][0]
            location_name = location_data['locationName']
            elements = location_data['weatherElement']

            # 建立元素對照表
            element_map = {el['elementName']: el['time'] for el in elements}

            # 格式化訊息
            lines = [f"*{location_name} 36 小時天氣預報*"]

            for i in range(3):
                start = element_map['Wx'][i]['startTime']
                end = element_map['Wx'][i]['endTime']
                period = self.get_period_name(start)

                wx = element_map['Wx'][i]['parameter']['parameterName']
                ci = element_map['CI'][i]['parameter']['parameterName']
                minT = element_map['MinT'][i]['parameter']['parameterName']
                maxT = element_map['MaxT'][i]['parameter']['parameterName']
                pop = element_map['PoP'][i]['parameter']['parameterName']

                lines.append("")
                lines.append(f"{period}({start[0:16]} ~ {end[11:16]})")
                lines.append(f"{wx},{ci}")
                lines.append(f"溫度:{minT}°C ~ {maxT}°C")
                lines.append(f"降雨:{pop}%")

            self.result = "\n".join(lines)
            return self.result

        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
            self.result = f"無法取得{self.location}天氣資料"
            return self.result

    def push(self):
        """推送天氣訊息到 LINE"""
        try:
            weather_line_bot = LineBot(self.result)
            weather_line_bot.push_message()
        except Exception as e:
            print(f"Failed to send weather info: {e}")


# 爬蟲
class WebCrawlerUSA:
    def __init__(self):
        self.rs = requests.session()
        self.urls = [
            ('道瓊指數', 'https://invest.cnyes.com/index/GI/DJI'),  # DJI
            ('S&P 500', 'https://invest.cnyes.com/index/GI/INX'),  # SPX
            ('費城半導體', 'https://invest.cnyes.com/index/GI/SOX'),  # 費城半導體
            ('那斯達克綜合指數', 'https://invest.cnyes.com/index/GI/IXIC'),  # NASDAQ
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
            info_percent = soup.select(
                '.jsx-2214436525.change-percent')[0].text
            if '+' in info_net:
                info = '{}▲  {}▲'.format(info_net, info_percent)
                info = info.replace('+', '')
            else:
                info = '{}▼  {}▼'.format(info_net, info_percent)
                info = info.replace('-', '')
            self.result.append(
                '{}\n{}\n{}\n{}'.format(info_date, url[0], info_price, info))

    def push(self):
        result = '\n'+'\n\n'.join(self.result)
        try:
            # LineOA - 美股資訊
            usa_stock_line_bot = LineBot(result)
            usa_stock_line_bot.push_message()
            # Slack
            slack = SlackNotification(result)
            slack.push()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # 美股資訊
    crawler = WebCrawlerUSA()
    crawler.fetch()
    crawler.push()

    # 氣象資訊
    weather = WeatherForecast(location='高雄市')
    weather.fetch()
    weather.push()
