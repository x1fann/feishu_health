import requests
from datetime import datetime

APP_ID = "cli_a72e91a3b8f9d013"
APP_SECRET = "KFPqPHB2p9wf1s9o43CGCAeTbuBJ4xSX"
APP_TOKEN = "OzOMbiyh5aDjk3socT9c74zsnEf"
TABLE_ID = "tblOqr0jzSA4HBTb"


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
        raise Exception(f"读取失败: {response.text}")


records = read_records(APP_TOKEN, TABLE_ID, {"page_size": 20})
print(records)


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
        raise Exception(f"更新失败: {response.text}")


# 获取每日最低温度
def get_daily_min_temp():
    weather_api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 31.2304,  # 上海的纬度
        "longitude": 121.4737,  # 上海的经度
        "daily": "temperature_2m_min",  # 获取每日最低温度
        "temperature_unit": "celsius",  # 单位：摄氏度
        "timezone": "Asia/Shanghai",  # 时区设置
    }
    response = requests.get(weather_api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["daily"]["temperature_2m_min"][0]
    else:
        raise Exception(f"获取天气数据失败: {response.text}")


# 新增一行数据到表格
def add_new_record():
    # 获取今天的最低温度
    min_temperature = get_daily_min_temp()

    today = datetime.today().strftime("%Y-%m-%d")
    today_unix_timestamp = int(datetime.strptime(
        today, "%Y-%m-%d").timestamp() * 1000)

    fields = {
        "日期": today_unix_timestamp,
        "最低气温": min_temperature,
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
