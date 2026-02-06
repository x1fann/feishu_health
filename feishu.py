import requests
import os
from datetime import datetime

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
APP_TOKEN = os.environ.get("APP_TOKEN")
TABLE_ID = os.environ.get("TABLE_ID")


# 获取access_token
def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, headers=headers, json=data)
    return response.json()["tenant_access_token"]


# 获取表格数据
def read_records(APP_TOKEN, TABLE_ID, params=None):
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["data"]["items"]
    else:
        raise Exception(f"读取表格失败: {response.text}")


records = read_records(APP_TOKEN, TABLE_ID, {"page_size": 20})
# print(records)


# 更新表格数据
def update_records(APP_TOKEN, TABLE_ID, record_id, fields):
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json"}
    data = {"fields": fields}

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        raise Exception(f"更新表格失败: {response.text}")

# 获取气温数据
def get_temp_for_days():
    weather_api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        # 上海 31.2304, 121.4737 
        # 杭州 30.2741, 120.1551
        # 高平 35.7980, 112.9239
        "latitude": 35.7980,  
        "longitude": 112.9239,  
        "daily": "temperature_2m_min,temperature_2m_max",  # 获取每日最低和最高气温
        "temperature_unit": "celsius",  # 单位：摄氏度
        "timezone": "Asia/Shanghai",  # 时区设置为上海  
        "past_days":"1" , # 获取过去一天的天气数据
        # 中国气象局模型 cma_grapes_global 
        # 美国NOAA gfs_seamless
        "models":"gfs_seamless" 
    }
    response = requests.get(weather_api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # 获取今天和昨天的最低气温
        min_temp_today = data["daily"]["temperature_2m_min"][1]
        min_temp_yesterday = data["daily"]["temperature_2m_min"][0]
        # 获取今天和昨天的最高气温
        max_temp_today = data["daily"]["temperature_2m_max"][1]
        max_temp_yesterday = data["daily"]["temperature_2m_max"][0]
        return min_temp_today, min_temp_yesterday, max_temp_today, max_temp_yesterday
    else:
        raise Exception(f"获取天气数据失败: {response.text}")


# 新增数据到表格
def add_new_record():
    # 获取温度数据
    min_temp_today, min_temp_yesterday, max_temp_today, max_temp_yesterday = get_temp_for_days()

    # 计算最低温度差值和最高温度差值
    min_temp_diff = round(min_temp_today - min_temp_yesterday, 1)
    max_temp_diff = round(max_temp_today - max_temp_yesterday, 1)
    
    # 取变化幅度较大的温差
    if abs(min_temp_diff) >= abs(max_temp_diff):
        temp_diff = min_temp_diff
    else:
        temp_diff = max_temp_diff

    today = datetime.today().strftime("%Y-%m-%d")
    today_unix_timestamp = int(datetime.strptime(
        today, "%Y-%m-%d").timestamp() * 1000)

    fields = {
        "日期": today_unix_timestamp,
        "最低气温": min_temp_today,
        "昨日温差": temp_diff
    }

    # 使用Feishu表格API新增记录
    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}",
               "Content-Type": "application/json"}
    data = {"fields": fields}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"新增记录成功: {response.json()}")
    else:
        raise Exception(f"新增记录失败: {response.text}")


if __name__ == "__main__":
    add_new_record()
