import requests
import json

# 设置请求头
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection": "keep-alive",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": "JSESSIONID=408E3005730E6E10B0B5AFCC665A3780; sto-id-20480=CELMMCMKFAAA; JSESSIONID=B10BC88A6144B8443D3C9C67F03B1D2E",
    "origin": "http://zhjw.qfnu.edu.cn",
    "referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36 Edg/132.0.0.0",
    "x-requested-with": "XMLHttpRequest",
}

data = {
    "sEcho": "1",
    "iColumns": "99999",
    "sColumns": "",
    "iDisplayStart": "0",
    "iDisplayLength": "99999",
    "mDataProp_0": "kch",
    "mDataProp_1": "kcmc",
    "mDataProp_2": "fzmc",
    "mDataProp_3": "ktmc",
    "mDataProp_4": "xf",
    "mDataProp_5": "skls",
    "mDataProp_6": "sksj",
    "mDataProp_7": "skdd",
    "mDataProp_8": "xqmc",
    "mDataProp_9": "ctsm",
    "mDataProp_10": "czOper",
}

# 目标URL
url = r"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk"

params = {
    "kcxx": "",
    "skls": "",
    "skxq": "",
    "skjc": "",
    "sfym": "false",
    "sfct": "false",
    "sfxx": "true",
}
# 发送POST请求
try:
    response = requests.post(url, headers=headers, data=data, params=params)
    # 将响应JSON写入文件，格式化，并使用utf-8编码，处理\u编码
    with open("response.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(response.json(), indent=4, ensure_ascii=False))
except requests.exceptions.RequestException as e:
    print(f"请求发生错误: {e}")
