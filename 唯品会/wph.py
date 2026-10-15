# -*- coding:utf-8 -*-
# Author: luoge
import requests
import hashlib


def hash(arg):
    md = hashlib.sha1()
    md.update(arg.encode())
    return md.hexdigest()


data = {
    "age_group": "",
    "androidTenSlotTabSupport": "1",
    "api_key": "23e7f28019e8407b98b84cd05b5aef2c",
    "app_name": "shop_android",
    "app_version": "7.45.6",
    "auto_refresh": "1",
    "changeResolution": "2",
    "channel_flag": "0_1",
    "channel_name": "运动",
    "city_id": "104104101",
    "client": "android",
    "client_type": "android",
    "darkmode": "0",
    "deeplink_cps": "",
    "device_model": "Pixel 4",
    "device_vendor": "google",
    "did": "0.0.f81256ac564e49764335a4919db82438.dd16b7",
    "fdc_area_id": "104104101",
    "function": "",
    "height": "2236",
    "load_more_token": "",
    "mars_cid": "73282cb2-beb4-377e-b817-e8fe6dfb9cec",
    "menu_code": "daohangyundong",
    "mobile_channel": "8rdlo74r:::",
    "mobile_platform": "3",
    "net": "WIFI",
    "os_type": "android",
    "os_version": "10",
    "otddid": "",
    "other_cps": "",
    "oxo_area_id": "",
    "oxo_city": "",
    "oxo_district": "",
    "oxo_province": "",
    "pageSessionId": "73282cb2-beb4-377e-b817-e8fe6dfb9cec_1764249596506",
    "page_id": "page_channel_1764247877787",
    "phone_model": "Pixel 4",
    "province_id": "104104",
    "referer": "com.achievo.vipshop.homepage.activity.MainActivity",
    "rom": "Dalvik/2.1.0 (Linux; U; Android 10; Pixel 4 Build/QQ2A.200405.005)",
    "sd_tuijian": "0",
    "service_provider": "",
    "session_id": "73282cb2-beb4-377e-b817-e8fe6dfb9cec_shop_android_1764247075934",
    "sex_type": "",
    "skey": "2d30297ff20ec9b7442dc4f3c335abdc",
    "source_app": "android",
    "standby_id": "8rdlo74r:::",
    "sys_version": "29",
    "timestamp": "1764249591",
    "warehouse": "VIP_NH",
    "width": "1080"
}

sa1 = "a84c5883206309ad076deea939e850dc"

salt = "&".join([f"{i}={data[i]}" for i in sorted(data.keys())])

res1 = hash(sa1 + salt)
print(res1)
sign = hash(sa1 + res1)
print(sign)


headers = {
    "Host": "mapi.appvipshop.com",
    "authorization": "OAuth api_sign=" + sign,
    "x-vip-host": "mapi.appvipshop.com",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "okhttp/3.12.13"
}
url = "https://mapi.appvipshop.com/vips-mobile/rest/layout/channel/data"
response = requests.post(url, headers=headers, data=data)
print(response.text)
print(response)
