"""
@User : 'cosmos'
@Date : '2025/2/13'
@Time : '下午11:57'
"""
import csv

import execjs
import requests
import re
import pandas
cookies = {
    'qgqp_b_id': '17ce4ba7fb740dad2828f4cf7e9697cc',
    'websitepoptg_api_time': '1739459190989',
    'st_si': '90045857175579',
    'st_asi': 'delete',
    'fullscreengg': '1',
    'fullscreengg2': '1',
    'st_pvi': '30256184217229',
    'st_sp': '2025-02-13%2023%3A06%3A31',
    'st_inirUrl': 'https%3A%2F%2Fwww.baidu.com%2Flink',
    'st_sn': '4',
    'st_psi': '20250213231357602-117001314791-8676583986',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # 'Cookie': 'qgqp_b_id=17ce4ba7fb740dad2828f4cf7e9697cc; websitepoptg_api_time=1739459190989;
    # st_si=90045857175579; st_asi=delete; fullscreengg=1; fullscreengg2=1; st_pvi=30256184217229;
    # st_sp=2025-02-13%2023%3A06%3A31; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=4;
    # st_psi=20250213231357602-117001314791-8676583986',
    'Referer': 'https://guba.eastmoney.com/',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 '
                  'Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
stock = []
for page in range(5):
    params = {
        'type': '0',
        'sort': '0',
        'page': page,
        'v': '2025_2_14_18_0',
    }
    # 第一次请求 获取服务器返回的密文数据
    response = requests.get('https://gbcdn.dfcfw.com/rank/popularityList.js', params=params, headers=headers)
    # print(response.text)
    data = re.findall(r"var popularityList='(.*?)'", response.text)[0]
    # print(data)

    # 读取js文件
    jscode = open('./JSDemo.js', 'r', encoding='utf-8').read()
    scriptData = execjs.compile(jscode).call('main', data)  # 调用js函数，获取返回结果
    # print(scriptData)
    lists = []
    for i in scriptData:
        # print(i)
        lists.append(i['code'])
    # print(lists)
    t123 = ','.join(lists)
    # print(t123)
    secids = execjs.compile(jscode).call('getHQSecIdByMutiCode', t123)
    # print(secids)


#  第二次请求 获取股票代码
    response = requests.get(
        'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&np=3&ut=a79f54e3d4c8d44e494efb8f748db291&invt=2'
        '&secids={}&fields=f1,f2,f3,f4,f12,f13,f14,f152,f15,f16'.format(
            secids),
        cookies=cookies,
        headers=headers,
    ).json()
    # print(response)  # 打印json格式的字符串
    for i in response['data']['diff']:  # 遍历股票代码
        print(i)
        print('***'*30)
        stock.append(i)
print('==='*40)
# print(stock)
# print('---'*40)

# ===============================================================================

# df = pandas.DataFrame(stock)  # 转换成DataFrame格式
# print(df)
# 保存为 CSV
# df.to_csv('股票1.csv', index=False, encoding='utf-8-sig')
# # print(df)
# print('数据已保存为 股票1.csv')


# # 构造列索引序列
# subjects = ['f1', 'f2', 'f3', 'f4', 'f12', 'f13', 'f14', 'f15', 'f152', 'f16']
# # 构造行索引序列
# stu = [f'第{str(i+1)}' for i in range(df.shape[0])]
# # 添加行、列索引
# data = pandas.DataFrame(stock, columns=subjects, index=stu)
# print(data)
# # 保存为 CSV
# data.to_csv('./股票2.csv', encoding='utf-8-sig')
# print('数据已保存为 股票2.csv')


# # 写入数据
# filename = '股票3.csv'
# with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
#     # 定义表头（字段名）最后两个字段名互换也行
#     fieldnames = ['f1', 'f2', 'f3', 'f4', 'f12', 'f13', 'f14', 'f15', 'f152', 'f16']
#     writer = csv.DictWriter(f, fieldnames=fieldnames)  # 创建一个 DictWriter 对象,fieldnames 为字段名要与数据对应
#     # 写入表头
#     writer.writeheader()
#     # 写入数据行
#     for item in stock:
#         writer.writerow(item)
# print(f'数据已保存到 {filename}')
