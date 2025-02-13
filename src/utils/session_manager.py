from requests import Session
import threading

# 全局session变量
_session = None
_session_lock = threading.Lock()


def init_session():
    """初始化全局会话"""
    global _session
    with _session_lock:
        if _session is None:
            _session = Session()
            _session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Connection": "keep-alive",
                }
            )
        return _session


def get_session():
    """获取当前会话，如果不存在则初始化"""
    global _session
    if _session is None:
        return init_session()
    return _session


def reset_session():
    """重置会话"""
    global _session
    with _session_lock:
        if _session is not None:
            _session.close()
        _session = None
