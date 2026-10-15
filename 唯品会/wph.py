# -*- coding:utf-8 -*-
# Author: luoge
import requests
import hashlib


def hash(arg):
    md = hashlib.sha1()
    md.update(arg.encode())
    return md.hexdigest()


data = {
    
}

sa1 = "密钥"

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
url = "https://mapi.appvipshop.com/接口
response = requests.post(url, headers=headers, data=data)
print(response.text)
print(response)
