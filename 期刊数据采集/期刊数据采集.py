"""
@User : 'cosmos'
@Date : '2025/10/28'
@Time : '下午8:45'
"""
import re
import csv
import json
import requests
# from curl_cffi import requests
from lxml import etree
import subprocess
# 在解密数据时如果出现编码报错则使用偏函数修改process默认编码
from functools import partial

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs

headers = {
    "accept": "text/html, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://qikan.cqvip.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://qikan.cqvip.com/Qikan/Journal/JournalGuid?from=index",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
first_url = "https://qikan.cqvip.com/Qikan/Journal/JournalGuid"
two_url = "https://qikan.cqvip.com/Search/SearchList"
params = {
    "from": "index"
}
requests = requests.session()


def first_request():
    try:
        response = requests.get(first_url, headers=headers, params=params, timeout=10)
        obj_html = etree.HTML(response.text)
        content_data = obj_html.xpath('//meta[2]/@content')[0]
        ts = obj_html.xpath('//script[1]/text()')[0]
        js_src = 'https://qikan.cqvip.com/' + re.findall('charset="utf-8" src="(.*?)" r=', response.text)[0]
        return content_data, ts, js_src
    except (requests.exceptions.RequestException, IndexError) as e:
        print(f"初始请求失败：{e}")
        return None, None, None


def two_request(content_data, func_code, js_src, writer):
    fun_code = requests.get(js_src, headers=headers).text
    # print(fun_code)
    with open('qk.js', encoding='utf-8') as f:
        js_code = f.read().replace('content123', content_data).replace(
            '!"sz_fun"', func_code).replace('"@func"', fun_code)
    open('test.js', 'w', encoding='utf-8').write(js_code)
    js = execjs.compile(js_code)
    for page in range(1, 3):
        cookie = js.call('RS_6')
        cookies = {
            cookie[0]: cookie[1]
        }
        # print(cookies)
        # 用字典定义搜索参数
        search_param = {
            "ObjectType": 7,
            "SearchKeyList": [],
            "SearchExpression": None,
            "BeginYear": None,
            "EndYear": None,
            "UpdateTimeType": None,
            "JournalRange": None,
            "DomainRange": None,
            "ClusterFilter": "ZY=8#哲学宗教",
            "ClusterLimit": 0,
            "ClusterUseType": "Article",
            "UrlParam": "",
            "Sort": "1",
            "SortField": None,
            "UserID": "0",
            "PageNum": page,  # 可动态修改页码
            "PageSize": 100,
            "SType": None,
            "StrIds": None,
            "IsRefOrBy": 0,
            "ShowRules": "",
            "IsNoteHistory": 0,
            "AdvShowTitle": None,
            "ObjectId": None,
            "ObjectSearchType": 0,
            "ChineseEnglishExtend": 0,
            "SynonymExtend": 0,
            "ShowTotalCount": 0,
            "AdvTabGuid": ""
        }
        # 转换为JSON字符串
        data = {"searchParamModel": json.dumps(search_param)}
        response = requests.post(two_url, headers=headers, cookies=cookies, data=data)
        response.encoding = 'utf-8'
        # print(response.text)
        get_data(response, cookies, writer)


def get_data(response, cookies, writer):
    html = etree.HTML(response.text)
    lists = html.xpath('//div[@class="cover-list"]/div')
    for i in lists:
        titles = i.xpath('./dl/dt')
        for data in titles:
            href = data.xpath('./a/@href')[0]
            href_url = f"https://qikan.cqvip.com{href}"
            response = requests.get(href_url, headers=headers, cookies=cookies)
            html = etree.HTML(response.text)
            base_url_list = html.xpath('//div[@class="object-info-content"]/a/@href')
            if not base_url_list:
                aaa = True
                while aaa:
                    try:
                        title = html.xpath('//div[@class="object-title"]//text()')[1].replace(" ", "").replace(
                            "\n", "").replace("\t", "").replace("\r", "")
                        print("未找到详情页链接")
                        dicts = {
                            '期刊名称': title,
                            '期刊详情': ''
                        }
                        save_data(dicts, writer)
                        aaa = False
                    except Exception as e:
                        print('继续获取')
                continue
            base_url = base_url_list[0]
            print(base_url)
            detail_url = f"https://qikan.cqvip.com{base_url}" + "&from=Qikan_Journal_Summary"
            print(detail_url)
            get_detail(detail_url, cookies, writer)


def get_detail(href, cookies, writer):
    response = requests.get(href, headers=headers, cookies=cookies)
    # print(response.text)
    # print(response.status_code)
    html = etree.HTML(response.text)
    title = html.xpath('//div[@class="object-title"]//text()')[1].replace(" ", "").replace("\n", "").replace(
        "\t", "").replace("\r", "")
    # print(title)
    detail = html.xpath('//div[@class="info-content"]//p//text()')[0].replace(" ", "").replace("\n", "").replace(
        "\t", "").replace("\r", "")
    # print(f'{title = },{detail = }')  # 期刊名称、期刊详情
    dicts = {
        '期刊名称': title,
        '期刊详情': detail
    }
    save_data(dicts, writer)


def save_data(data_dict, writer):
    writer.writerow(data_dict)
    print(f"CSV 保存成功: {data_dict['期刊名称']}")


# 在main函数中打开文件，传递给save_data
if __name__ == '__main__':
    with open('期刊数据采集.csv', 'a', encoding='utf-8', newline='') as csv_file:
        field_names = ['期刊名称', '期刊详情']
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        if csv_file.tell() == 0:
            csv_writer.writeheader()
        # 传递csv_writer给后续函数
        content, ts_code, js_url = first_request()
        two_request(content, ts_code, js_url, csv_writer)  # 新增参数传递
