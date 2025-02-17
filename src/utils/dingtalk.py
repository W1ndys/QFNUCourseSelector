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
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        webhook = config.get("dingtalk_webhook")
        secret = config.get("dingtalk_secret")
        if not webhook:
            logging.info("未配置钉钉 webhook，跳过发送通知")
            return None, None
        return webhook, secret
    except FileNotFoundError:
        logging.info("未找到配置文件，跳过发送通知")
        return None, None


# 推送到钉钉
def dingtalk(title, content):
    try:
        dingtalk_webhook, dingtalk_secret = get_dingtalk_config()
        if not dingtalk_webhook:
            return None

        headers = {"Content-Type": "application/json"}
        # 美化markdown消息格式
        formatted_content = (
            f"### {title}\n\n"
            f"---\n\n"  # 添加分隔线
            f"{content}\n\n"
            f"---\n\n"  # 添加底部分隔线
            f"*发送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}*"  # 添加发送时间
        )

        # 使用钉钉的Markdown语法将"失败"显示为红色并加粗，"成功"显示为绿色并加粗
        formatted_content = formatted_content.replace(
            "失败", "<font color='red'>失败</font>"
        )
        formatted_content = formatted_content.replace(
            "成功", "<font color='green'>成功</font>"
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
        "测试消息",
        "这是一条测试消息，如果你看到这条消息，证明dingtalk的webhook无问题成功失败",
    )
