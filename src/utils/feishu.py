import time
import hmac
import hashlib
import base64
import requests
import json
import logging


# 读取config.json获取飞书webhook和secret
def get_feishu_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        webhook = config.get("feishu_webhook")
        secret = config.get("feishu_secret")
        if not webhook:
            logging.info("未配置飞书 webhook，跳过发送通知")
            return None, None
        return webhook, secret
    except FileNotFoundError:
        logging.info("未找到配置文件，跳过发送通知")
        return None, None


def feishu(title: str, content: str) -> dict:
    """
    发送飞书机器人消息

    Args:
        webhook_url: 飞书机器人的webhook地址
        secret: 安全设置中的签名校验密钥
        title: 消息标题
        content: 消息内容

    Returns:
        dict: 接口返回结果
    """
    feishu_webhook, feishu_secret = get_feishu_config()
    timestamp = str(int(time.time()))

    # 计算签名
    string_to_sign = f"{timestamp}\n{feishu_secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建消息内容
    msg = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [[{"tag": "text", "text": content}]],
                }
            }
        },
    }

    # 发送请求
    try:
        if not isinstance(feishu_webhook, str):
            return {"error": "飞书webhook未配置"}
        response = requests.post(feishu_webhook, headers=headers, data=json.dumps(msg))
        return response.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    feishu("测试", "测试内容")
