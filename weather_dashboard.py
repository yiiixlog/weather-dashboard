import streamlit as st
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "CWA-9F550D29-DC8A-43EF-B0A7-02B5BC5F2A31"

CITIES = [
    "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣",
    "苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市",
    "嘉義縣", "臺南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣",
    "臺東縣", "澎湖縣", "金門縣", "連江縣"
]

def get_weather(city):
    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
        f"?Authorization={API_KEY}&locationName={city}"
    )
    res = requests.get(url, verify=False)
    return res.json()

st.title("🌤️ 台灣氣象資料 Dashboard")

city = st.selectbox("選擇城市", CITIES)

try:
    data = get_weather(city)

    # --- 安全提取資料 ---
    location = data["records"]["location"][0]
    elements = {elem["elementName"]: elem["time"][0]["parameter"]["parameterName"]
                for elem in location["weatherElement"]}

    weather = elements.get("Wx", "資料缺失")
    rain = elements.get("PoP", "資料缺失")
    min_temp = elements.get("MinT", "資料缺失")
    max_temp = elements.get("MaxT", "資料缺失")
    comfort = elements.get("CI", "資料缺失")

    # --- UI 輸出 ---
    st.subheader(f"{city} 未來 12 小時天氣預報")
    st.success(f"🌈 天氣：{weather}")
    st.info(f"🌧 降雨機率：{rain}%")
    st.warning(f"🌡 氣溫：{min_temp}°C ～ {max_temp}°C")
    st.write(f"🙂 舒適度：{comfort}")

except Exception as e:
    st.error(f"發生錯誤：{e}")
