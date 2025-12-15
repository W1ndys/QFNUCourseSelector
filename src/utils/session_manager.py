import httpx
import asyncio
from typing import Optional

# 全局session变量
_session: Optional[httpx.AsyncClient] = None
_session_lock = asyncio.Lock()


async def init_session():
    """初始化全局会话"""
    global _session
    async with _session_lock:
        if _session is None:
            _session = httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Connection": "keep-alive",
                },
                follow_redirects=True,
                timeout=30.0
            )
        return _session


async def get_session():
    """获取当前会话, 如果不存在则初始化"""
    global _session
    if _session is None:
        return await init_session()
    return _session


async def reset_session():
    """重置会话"""
    global _session
    async with _session_lock:
        if _session is not None:
            await _session.aclose()
        _session = None
