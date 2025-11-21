# 🌦️ 台灣氣象資料 Dashboard

一個使用 **Streamlit** 與 **中央氣象署 CWA Open Data API** 打造的互動式天氣儀表板
可查詢 **全台各縣市** 未來 **12 小時天氣預報**，包含：

- 天氣概況（☀️ 🌥️ 🌧️）
- 降雨機率
- 氣溫範圍
- 舒適度指標

介面簡潔、好讀，適合作為資料分析、練習 API、或前端展示用小工具

---

## 🚀 功能特色

- **全台縣市下拉選單**  
- 自動抓取中央氣象署 API 資料  
- 以視覺化卡片方式呈現資訊：
  - 🌤️ 天氣狀況  
  - 🌧️ 降雨機率  
  - 🌡️ 氣溫區間  
  - 😊 舒適度  
- 介面使用 Streamlit，部署容易、支援手機瀏覽

---

## 🧩 使用技術

| 技術 | 用途 |
|------|------|
| Python 3.13 | 主程式語言 |
| Streamlit | UI 介面呈現 |
| Requests | 呼叫 CWA API |
| CWA Open Data API | 天氣資料來源 |
| Pandas | 資料處理（可擴展） |

---

## 📦 安裝與執行方式

### 1️⃣ Clone 專案
```bash
git clone https://github.com/yiiixlog/weather-dashboard.git
cd weather-dashboard
```

### 2️⃣ 安裝所需套件
```bash
pip install -r requirements.txt
```

### 3️⃣ 執行 Streamlit App
```bash
streamlit run weather_dashboard.py
```

---

## 🔑 中央氣象署 API 使用

本專案使用中央氣象署：

- **未來 12 小時天氣預報 API**
- DataID：`F-C0032-001`
- 官方文件：https://opendata.cwa.gov.tw/

請在程式中加入你的 API 金鑰：

```python
API_KEY = "你的授權碼"
```

---

## 🖼️ 介面預覽

（你可以在 repo 建立 `/images/demo.png` 後放入）

```markdown
![demo](images/demo.png)
```

---

✨ A weather app that makes checking Taiwan’s forecast beautifully simple.

