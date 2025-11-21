"""
LINE Flex Message 模板
"""
from linebot.models import FlexSendMessage


def create_stock_flex_message(stocks_data):
    """
    建立美股資訊的 Flex Message

    Args:
        stocks_data: list of dict, 每個 dict 包含:
            - name: 股票名稱
            - date: 日期
            - price: 價格
            - change: 漲跌點數
            - percent: 漲跌百分比
            - trend: 'up' or 'down'
    """
    contents = []
    for i, stock in enumerate(stocks_data):
        trend_color = "#FF4444" if stock["trend"] == "down" else "#00C851"
        trend_icon = "▼" if stock["trend"] == "down" else "▲"

        stock_box = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": stock["name"],
                            "weight": "bold",
                            "size": "md",
                            "color": "#1DB446",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": stock["date"],
                            "size": "xs",
                            "color": "#999999",
                            "align": "end"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": stock["price"],
                            "size": "xl",
                            "weight": "bold",
                            "color": "#333333"
                        }
                    ],
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{trend_icon} {stock['change']}",
                            "size": "sm",
                            "color": trend_color,
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"{trend_icon} {stock['percent']}",
                            "size": "sm",
                            "color": trend_color,
                            "margin": "md"
                        }
                    ],
                    "margin": "sm"
                }
            ],
            "paddingAll": "15px",
            "backgroundColor": "#F8F8F8" if i % 2 == 0 else "#FFFFFF",
            "cornerRadius": "10px",
            "margin": "sm" if i > 0 else "none"
        }
        contents.append(stock_box)

    flex_message = FlexSendMessage(
        alt_text="📊 美股日報",
        contents={
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 美股日報",
                        "color": "#ffffff",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": "US Stock Market",
                        "color": "#ffffff",
                        "size": "xs",
                        "margin": "xs"
                    }
                ],
                "backgroundColor": "#1E90FF",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "15px"
            },
            "styles": {
                "header": {
                    "backgroundColor": "#1E90FF"
                }
            }
        }
    )
    return flex_message


def create_weather_flex_message(location_name, weather_data):
    """
    建立天氣預報的 Flex Message - V3 緊湊卡片風格

    Args:
        location_name: 地點名稱
        weather_data: list of dict, 每個 dict 包含:
            - period: 時段名稱
            - emoji: emoji 圖示
            - time: 時間範圍
            - weather: 天氣狀況
            - comfort: 舒適度
            - minTemp: 最低溫度
            - maxTemp: 最高溫度
            - rain: 降雨機率
    """
    # 建立天氣項目
    contents = [
        {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"🌤️ {location_name}天氣",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#2C3E50"
                },
                {
                    "type": "text",
                    "text": "36 小時預報",
                    "size": "xs",
                    "color": "#95A5A6",
                    "margin": "xs"
                }
            ],
            "paddingBottom": "15px"
        },
        {
            "type": "separator"
        }
    ]

    for i, weather in enumerate(weather_data):
        # 降雨機率顏色
        rain_percent = int(weather["rain"])
        if rain_percent >= 70:
            rain_color = "#E53935"
        elif rain_percent >= 30:
            rain_color = "#FB8C00"
        else:
            rain_color = "#43A047"

        # 卡片式設計
        weather_card = {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # 標題列: emoji + 時段 + 時間
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": weather["emoji"],
                            "size": "lg",
                            "flex": 0,
                            "margin": "none"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": weather["period"],
                                    "weight": "bold",
                                    "size": "md",
                                    "color": "#2C3E50"
                                },
                                {
                                    "type": "text",
                                    "text": weather["time"],
                                    "size": "xxs",
                                    "color": "#95A5A6"
                                }
                            ],
                            "margin": "md"
                        }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                # 天氣資訊
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": weather["weather"],
                            "size": "sm",
                            "color": "#34495E",
                            "weight": "bold",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": weather["comfort"],
                            "size": "xs",
                            "color": "#7F8C8D",
                            "margin": "xs",
                            "wrap": True
                        }
                    ],
                    "margin": "md"
                },
                # 溫度和降雨 - 並排顯示
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌡️",
                                    "size": "sm",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": f"{weather['minTemp']}° - {weather['maxTemp']}°",
                                    "size": "sm",
                                    "weight": "bold",
                                    "color": "#FF6B35",
                                    "margin": "sm",
                                    "flex": 0
                                }
                            ],
                            "flex": 1
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💧",
                                    "size": "sm",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": f"{weather['rain']}%",
                                    "size": "sm",
                                    "weight": "bold",
                                    "color": rain_color,
                                    "margin": "sm",
                                    "flex": 0
                                }
                            ],
                            "flex": 1
                        }
                    ],
                    "margin": "md",
                    "spacing": "md"
                }
            ],
            "backgroundColor": "#FAFAFA",
            "cornerRadius": "10px",
            "paddingAll": "15px",
            "margin": "md"
        }
        contents.append(weather_card)

    flex_message = FlexSendMessage(
        alt_text=f"🌤️ {location_name} 36 小時天氣預報",
        contents={
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px"
            },
            "styles": {
                "body": {
                    "backgroundColor": "#FFFFFF"
                }
            }
        }
    )
    return flex_message
