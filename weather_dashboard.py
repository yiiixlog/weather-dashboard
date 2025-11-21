import streamlit as st
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# --- 導入最新的 Google Gemini SDK 語法 ---
# 採用您測試成功的 genai.Client 結構
from google import genai 

# --- 1. 環境變數和 API 金鑰設定 ---
# 在本地運行時，從 .env 檔案載入變數
if 'STREAMLIT_CLOUD' not in os.environ: 
    load_dotenv()

# 確保 API 金鑰已設定
CWA_API_KEY = os.getenv("CWA_API_KEY") 
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# 修正：使用您測試成功的最新模型名稱
GEMINI_MODEL = "gemini-2.5-flash" 

if not CWA_API_KEY or not GEMINI_KEY:
    st.error("🚨 錯誤：CWA_API_KEY 或 GEMINI_API_KEY 遺失。")
    st.markdown("請確認您已在專案根目錄創建了 **.env** 檔案，並填入金鑰。")
    st.stop()

# --- 2. 初始化 Gemini 模型 (使用最新的 genai.Client 語法) ---
try:
    # 使用最新的 Client 語法進行初始化
    client = genai.Client(api_key=GEMINI_KEY)
except Exception as e:
    st.error(f"🚨 Gemini Client 初始化失敗: {e}")
    st.stop()


# --- 3. CWA API 資料獲取函數 ---
@st.cache_data(ttl=3600) # 緩存數據一小時
def get_weather_forecast(location_name):
    """
    從中央氣象署獲取未來 12 小時的天氣預報資料。
    資料項目代碼: F-C0032-001 (縣市天氣預報 - 36 小時)
    """
    # 修正：使用修正後的資料代碼 F-C0032-001
    DATA_ID = "F-C0032-001"
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{DATA_ID}"
    params = {
        "Authorization": CWA_API_KEY,
        "locationName": location_name,
        "elementName": "Wx,PoP,MinT,MaxT,CI"  # 天氣現象、降雨機率、最低溫、最高溫、舒適度
    }

    try:
        # 修正：由於您遇到 SSL 憑證驗證失敗，強制關閉驗證 (verify=False)。
        # ⚠️ 這是臨時措施，建議在安全環境中修復憑證問題。
        response = requests.get(url, params=params, verify=False) 
        response.raise_for_status() 
        data = response.json()

        if data.get('success') != 'true':
            st.error(f"❌ CWA API 呼叫失敗：{data.get('message', '未知錯誤')}")
            return None

        # F-C0032-001 的結構處理
        location_data = data['records']['location'][0]
        weather_elements = location_data['weatherElement']
        
        forecast = {
            "location": location_data['locationName'],
            "time": [],
            "data": {}
        }
        
        # 提取前兩段預報的時間 (對應未來 12 小時)
        time_data = weather_elements[0]['time'][:2] 
        
        for t in time_data:
            start_time = datetime.strptime(t['startTime'], '%Y-%m-%d %H:%M:%S').strftime('%m/%d %H:%M')
            end_time = datetime.strptime(t['endTime'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            forecast['time'].append(f"{start_time} - {end_time}")

        for element in weather_elements:
            element_name = element['elementName']
            forecast['data'][element_name] = [
                time_entry['parameter']['parameterName'] 
                for time_entry in element['time'][:2]
            ]
            
        return forecast

    except requests.exceptions.HTTPError as errh:
        st.error(f"❌ CWA API 網路錯誤 (HTTP {response.status_code}): {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"❌ CWA API 連線錯誤: {errc}")
    except Exception as e:
        st.error(f"❌ 處理 CWA 資料時發生錯誤: {e}")
    return None

# --- 4. Gemini AI 分析函數 ---
def get_ai_analysis(forecast_data):
    """使用 Gemini 模型對天氣預報進行摘要和溫馨提示。"""
    
    # 格式化天氣數據以便 AI 閱讀
    formatted_data = f"地點：{forecast_data['location']}\n"
    for i, time_range in enumerate(forecast_data['time']):
        formatted_data += f"\n--- 時間段 {i+1}: {time_range} ---\n"
        for key, values in forecast_data['data'].items():
            unit = ""
            if key in ["MinT", "MaxT"]: unit = "°C"
            if key == "PoP": unit = "%"

            if i < len(values): 
                formatted_data += f"- {key} ({get_element_name_chinese(key)}): {values[i]}{unit}\n"
    
    analysis_prompt = f"""
    請根據以下的天氣預報資料，以**溫暖、親切、且口語化**的語氣，為用戶提供一份簡短的摘要和實用建議。
    重點放在**未來 12 小時內**的天氣狀況。
    
    1. 摘要：總結天氣現象 (Wx)、溫度範圍 (MinT/MaxT) 和降雨機率 (PoP)。
    2. 建議：根據天氣給予穿著、交通或活動上的溫馨提示。
    3. **務必使用繁體中文回覆。**

    --- 天氣資料 ---
    {formatted_data}
    """
    
    try:
        # 使用您測試成功的最新 generate_content 呼叫方式
        response = client.models.generate_content(
            model=GEMINI_MODEL, 
            contents=analysis_prompt
        )
        return response.text.strip()
    except Exception as e:
        # 捕獲所有 Gemini API 錯誤
        st.error(f"❌ Gemini 服務發生錯誤: {e}")
        return "很抱歉，AI 服務發生了錯誤，無法提供天氣分析。請檢查您的金鑰或網路連線。"

# --- 5. 輔助函數 (轉換英文代碼為中文) ---
def get_element_name_chinese(code):
    """將天氣代碼轉換為中文名稱"""
    mapping = {
        "Wx": "天氣現象",
        "PoP": "降雨機率",
        "MinT": "最低溫度",
        "MaxT": "最高溫度",
        "CI": "舒適度指數"
    }
    return mapping.get(code, code)

# --- 6. Streamlit 介面配置 ---
TAIWAN_CITIES = [
    "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣", "臺中市", 
    "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣", 
    "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
]

def main():
    st.set_page_config(page_title="Gemini 天氣洞察儀表板", layout="wide")

    st.title("☀️ Taiwan 天氣儀表板")
    st.markdown("---")
    
    # 溫和的問候語氣
    st.markdown("### 🙋‍♀️ Hello！挑一個你想查詢天氣的地區吧")

    # 區域選擇
    selected_city = st.selectbox(
        "請選擇您想查詢的縣市：",
        options=["請選擇"] + TAIWAN_CITIES,
        index=0,
        key="city_selector"
    )

    if selected_city != "請選擇":
        st.subheader(f"📍 {selected_city} 的天氣預報與 AI 洞察")
        
        # 獲取天氣數據
        with st.spinner(f"正在從中央氣象署獲取 {selected_city} 的最新預報..."):
            forecast = get_weather_forecast(selected_city)

        if forecast:
            # --- 顯示天氣預報 ---
            st.markdown("#### ⏳ 未來 12 小時")
            
            col1, col2 = st.columns(2)
            
            time_range = forecast['time'][0]
            with col1:
                st.metric(label="預報時間範圍", value=time_range)
            
            min_temp = forecast['data']['MinT'][0]
            max_temp = forecast['data']['MaxT'][0]
            with col2:
                st.metric(label="溫度區間", value=f"{min_temp}°C ~ {max_temp}°C")
            
            st.info(
                f"**🌤️ 天氣現象:** {forecast['data']['Wx'][0]} | "
                f"**☔ 降雨機率 (PoP):** {forecast['data']['PoP'][0]}%"
            )

            # --- 獲取 Gemini AI 分析 ---
            st.markdown("#### 🤖 Gemini AI 洞察與貼心提醒")
            with st.spinner("正在呼叫 AI 進行專業分析與總結..."):
                analysis_text = get_ai_analysis(forecast)
            
            st.markdown(
                f"""
                <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #4682b4;'>
                    {analysis_text}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            st.caption(f"數據來源：中央氣象署，最後更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            st.warning("⚠️ 無法獲取該地區的最新天氣數據，請稍後再試。")
            
    else:
        st.info("👆 請從上方的下拉選單中選擇一個縣市來查看天氣預報和 AI 洞察。")

if __name__ == "__main__":
    main()