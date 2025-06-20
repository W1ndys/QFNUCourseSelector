import requests


def simulate_course_selection_request_with_string_cookie():
    """
    模拟向曲阜师范大学教务系统发送课程查询请求。
    此版本直接在请求头中使用字符串形式的Cookie。
    """
    # 1. 定义请求URL
    encoded_kcxx = "085099"
    url = "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk"

    # URL的查询参数
    params = {
        "kcxx": encoded_kcxx,
        "skls": "",
        "skxq": "",
        "skjc": "",
        "sfym": "false",
        "sfct": "false",
        "sfxx": "false",
        "skxq_xx0103": "",
        "kzyxkbx": "0",
        "kzyxkxx": "0",
        "kzyxkrx": "0",
        "kzyxkqt": "0",
    }

    # 2. 自定义Cookie字符串
    # ！！！在这里粘贴你从浏览器复制的完整Cookie字符串！！！
    # 格式通常是 "key1=value1; key2=value2; ..."
    cookie_string = ""

    # 3. 定义请求头 (Headers)
    # 将Cookie字符串直接加入到请求头中
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://zhjw.qfnu.edu.cn",
        "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Host": "zhjw.qfnu.edu.cn",
        # 直接将Cookie字符串作为'Cookie'头的值
        "Cookie": cookie_string,
    }

    # 4. 定义POST请求的表单数据 (Form Data / Payload)
    payload = {
        "sEcho": "1",
        "iColumns": "12",
        "sColumns": "",
        "iDisplayStart": "0",
        "iDisplayLength": "15",
        "mDataProp_0": "kch",
        "mDataProp_1": "kcmc",
        "mDataProp_2": "fzmc",
        "mDataProp_3": "xf",
        "mDataProp_4": "skls",
        "mDataProp_5": "sksj",
        "mDataProp_6": "skdd",
        "mDataProp_7": "xqmc",
        "mDataProp_8": "xkrs",
        "mDataProp_9": "syrs",
        "mDataProp_10": "ctsm",
        "mDataProp_11": "czOper",
    }

    try:
        # 5. 发送POST请求
        # 注意：这次我们不再使用 cookies 参数，因为Cookie信息已经包含在 headers 中了
        print("--- 正在发送POST请求 (使用字符串Cookie) ---")
        response = requests.post(
            url, params=params, headers=headers, data=payload, timeout=10
        )

        response.raise_for_status()

        # 6. 打印响应结果
        print("--- 请求成功 ---")
        try:
            print("响应内容 (JSON):")
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("响应内容 (非JSON):")
            print(response.text)
        print("------------------")

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")


# 执行函数
if __name__ == "__main__":
    simulate_course_selection_request_with_string_cookie()
