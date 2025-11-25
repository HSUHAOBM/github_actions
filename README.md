# Daily Notify - 每日通知

自動爬取美股資訊與台灣天氣預報，透過 LINE Bot 和 Slack 發送每日通知。

## 功能

- **美股資訊**：爬取道瓊、S&P 500、費城半導體、那斯達克等指數
- **天氣預報**：透過中央氣象署 API 取得 36 小時天氣預報
- **LINE Bot**：使用 Flex Message 卡片式訊息
- **Slack 通知**：同步發送到 Slack 頻道
- **自動排程**：每天台灣時間 06:00 自動執行

## 專案結構

```
daily_notify/
├── run.py                 # 主程式
├── flex_templates.py      # LINE Flex Message 模板
├── requirements.txt       # Python 套件依賴
└── (其他測試檔案...)

.github/
└── workflows/
    └── crawler.yml        # GitHub Actions 設定檔
```

## 環境變數設定

在 GitHub Repository 的 Settings > Secrets 中設定以下變數：

| 變數名稱 | 說明 |
|---------|------|
| `LINE_BOT_TOKEN` | LINE Bot Channel Access Token |
| `LINE_USER_ID` | LINE 接收訊息的 User ID |
| `CWA_API_KEY` | 中央氣象署 OpenData API Key |
| `SLACK_WEBHOOK` | Slack Incoming Webhook URL |



## GitHub Actions 排程

用 GitHub Actions 執行排程：

- **觸發時機**：每天 UTC 22:00（台灣時間 06:00）


