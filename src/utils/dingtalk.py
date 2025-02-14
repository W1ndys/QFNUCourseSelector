import requests
import json
import time
import hmac
import hashlib
import urllib
import base64
import urllib.parse
import logging


# 读取config.json获取钉钉webhook和secret
def get_dingtalk_config():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["dingtalk_webhook"], config["dingtalk_secret"]


# 推送到钉钉
def dingtalk(title, content):
    try:
        dingtalk_webhook, dingtalk_secret = get_dingtalk_config()

        headers = {"Content-Type": "application/json"}
        # 美化markdown消息格式
        formatted_content = (
            f"### {title}\n\n"
            f"---\n\n"  # 添加分隔线
            f"{content}\n\n"
            f"---\n\n"  # 添加底部分隔线
            f"*发送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}*"  # 添加发送时间
        )

        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": formatted_content},
        }

        if dingtalk_secret:
            timestamp = str(round(time.time() * 1000))
            secret_enc = dingtalk_secret.encode("utf-8")
            string_to_sign = f"{timestamp}\n{dingtalk_secret}"
            string_to_sign_enc = string_to_sign.encode("utf-8")
            hmac_code = hmac.new(
                secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(
                base64.b64encode(hmac_code).decode("utf-8").strip()
            )
            dingtalk_webhook = f"{dingtalk_webhook}&timestamp={timestamp}&sign={sign}"

        response = requests.post(
            dingtalk_webhook, headers=headers, data=json.dumps(payload)
        )

        try:
            data = response.json()
            if response.status_code == 200 and data.get("errcode") == 0:
                logging.info("钉钉发送通知消息成功🎉")
            else:
                logging.error(f"钉钉发送通知消息失败😞\n{data.get('errmsg')}")
        except Exception as e:
            logging.error(f"钉钉发送通知消息失败😞\n{e}")

        return response.json()
    except Exception as e:
        logging.error(f"钉钉发送通知消息失败😞\n{e}")


if __name__ == "__main__":
    dingtalk(
        "测试消息", "这是一条测试消息，如果你看到这条消息，证明dingtalk的webhook无问题"
    )
