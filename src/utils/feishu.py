import httpx
import json
from loguru import logger


# 读取config.json获取飞书webhook
def get_feishu_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        webhook = config.get("feishu_webhook")
        if not webhook:
            logger.info("未配置飞书 webhook, 跳过发送通知")
            return None
        return webhook
    except FileNotFoundError:
        logger.info("未找到配置文件, 跳过发送通知")
        return None


async def feishu(title: str, content: str) -> dict:
    """
    发送飞书机器人消息

    Args:
        title: 消息标题
        content: 消息内容

    Returns:
        dict: 接口返回结果
    """
    feishu_webhook = get_feishu_config()

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建消息内容
    msg = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title,
                },
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content,
                    },
                }
            ],
        },
    }

    # 发送请求
    try:
        if not isinstance(feishu_webhook, str):
            return {"error": "飞书webhook未配置"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(feishu_webhook, headers=headers, json=msg)
            return response.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import asyncio
    asyncio.run(feishu("测试", "测试内容"))
