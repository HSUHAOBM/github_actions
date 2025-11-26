import requests
import json
import os
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from datetime import datetime, timedelta
import urllib3
from flex_templates import create_stock_flex_message, create_weather_flex_message

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Slack
slack_webhook = os.getenv('SLACK_WEBHOOK')
# LineBot
line_bot_token = os.getenv('LINE_BOT_TOKEN')
line_user_id = os.getenv('LINE_USER_ID')
# 氣象署 API
cwa_api_key = os.getenv('CWA_API_KEY')


# LineBot
class LineBot:
    def __init__(self, context=None, flex_message=None):
        self.context = context
        self.flex_message = flex_message
        self.line_bot_api = LineBotApi(line_bot_token)
        self.user_id = line_user_id

    def push_message(self):
        if not self.user_id or not self.line_bot_api:
            raise Exception("LINE Bot token or user ID is missing.")
        try:
            # 如果有 Flex Message 就用 Flex,否則用純文字
            if self.flex_message:
                self.line_bot_api.push_message(self.user_id, self.flex_message)
            else:
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
        self.weather_data = []  # 儲存結構化資料用於 Flex Message

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
        if not cwa_api_key:
            print("Warning: CWA_API_KEY not set")
            self.result = "無法取得天氣資料：API Key 未設定"
            return self.result

        params = {
            'Authorization': cwa_api_key,
            'locationName': self.location
        }
        try:
            # 禁用 SSL 驗證以避免 GitHub Actions 環境的憑證問題
            response = requests.get(self.api_url, params=params, verify=False)
            response.raise_for_status()
            data = response.json()

            location_data = data['records']['location'][0]
            location_name = location_data['locationName']
            elements = location_data['weatherElement']

            # 建立元素對照表
            element_map = {el['elementName']: el['time'] for el in elements}

            # 格式化訊息
            lines = [f"*{location_name} 36 小時天氣預報*"]
            self.weather_data = []  # 清空並重新填充

            # 取得今天的日期用於比對
            from datetime import datetime as dt

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

                # 儲存結構化資料用於 Flex Message
                emoji_map = {"🌅 早上": "🌅", "☀️ 白天": "☀️",
                             "🌃 晚上": "🌃", "🌙 凌晨": "🌙"}
                period_text = period.replace(
                    emoji_map.get(period, ""), "").strip()

                # 第 3 個時段(索引 2)如果是"早上",加上"明天"前綴
                if i == 2 and "早上" in period_text:
                    period_text = "明天" + period_text

                self.weather_data.append({
                    "period": period_text,
                    "emoji": emoji_map.get(period, "🌤️"),
                    "time": f"{start[5:16]} - {end[5:16]}",
                    "weather": wx,
                    "comfort": ci,
                    "minTemp": minT,
                    "maxTemp": maxT,
                    "rain": pop
                })

            self.result = "\n".join(lines)
            return self.result

        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
            self.result = f"無法取得{self.location}天氣資料"
            return self.result

    def push(self):
        """推送天氣訊息到 LINE"""
        if not self.result or "無法取得" in self.result or "未設定" in self.result:
            print(f"Skipping weather notification: {self.result}")
            return
        try:
            # 使用 Flex Message
            flex_msg = create_weather_flex_message(
                self.location, self.weather_data)
            weather_line_bot = LineBot(flex_message=flex_msg)
            weather_line_bot.push_message()
            print("Weather message sent successfully")
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
        self.stocks_data = []  # 儲存結構化資料用於 Flex Message

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

            # 判斷漲跌
            if '+' in info_net:
                info = '{}▲  {}▲'.format(info_net, info_percent)
                info = info.replace('+', '')
                trend = 'up'
                change = info_net.replace('+', '')
                percent = info_percent.replace('+', '')
            else:
                info = '{}▼  {}▼'.format(info_net, info_percent)
                info = info.replace('-', '')
                trend = 'down'
                change = info_net.replace('-', '')
                percent = info_percent.replace('-', '')

            # 儲存文字格式
            self.result.append(
                '{}\n{}\n{}\n{}'.format(info_date, url[0], info_price, info))

            # 儲存結構化資料用於 Flex Message
            self.stocks_data.append({
                "name": url[0],
                "date": info_date,
                "price": info_price,
                "change": change,
                "percent": percent,
                "trend": trend
            })

    def push(self):
        try:
            # LineOA - 美股資訊 (使用 Flex Message)
            flex_msg = create_stock_flex_message(self.stocks_data)
            usa_stock_line_bot = LineBot(flex_message=flex_msg)
            usa_stock_line_bot.push_message()

            # Slack (使用文字格式)
            result = '\n'+'\n\n'.join(self.result)
            slack = SlackNotification(result)
            slack.push()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    # 美股資訊
    try:
        print("=" * 50)
        print("開始執行美股資訊爬蟲...")
        print("=" * 50)
        crawler = WebCrawlerUSA()
        crawler.fetch()
        crawler.push()
        print("美股資訊推送完成")
    except Exception as e:
        print(f"美股資訊執行失敗: {e}")

    # 氣象資訊
    try:
        print("\n" + "=" * 50)
        print("開始執行氣象資訊...")
        print("=" * 50)
        weather = WeatherForecast(location='高雄市')
        weather.fetch()
        weather.push()
        print("氣象資訊推送完成")
    except Exception as e:
        print(f"氣象資訊執行失敗: {e}")
