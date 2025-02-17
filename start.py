import json
import os
import time
import subprocess
from datetime import datetime, timedelta

CONFIG_PATH = "config.json"

def create_default_config():
    """创建符合严格JSON格式的默认配置文件"""
    default_config = {
        "schedule_time": "09:00",
        "user_account": "",
        "user_password": "",
        "select_semester": "",
        "mode": "fast",
        "courses": [
            {"course_id_or_name": "", "teacher_name": ""},
            {"course_id_or_name": "", "teacher_name": ""},
            {"course_id_or_name": "", "teacher_name": ""}
        ]
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)

def load_config():
    """加载并验证JSON格式"""
    if not os.path.exists(CONFIG_PATH):
        create_default_config()
        raise FileNotFoundError(f"配置文件 {CONFIG_PATH} 不存在，已生成默认配置，请填写后重试")

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误，请检查 {CONFIG_PATH} 文件（错误详情：{str(e)}）")

def validate_required_fields(config: dict):
    """验证必填字段"""
    required = ["schedule_time", "user_account", "user_password"]
    missing = [field for field in required if not config.get(field)]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")

def parse_schedule_time(time_str: str) -> datetime:
    """解析时间并验证有效性"""
    try:
        target_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise ValueError("时间格式错误，请使用 HH:MM 格式（例如 09:00）")

    target_datetime = datetime.combine(datetime.now().date(), target_time)
    if target_datetime <= datetime.now():
        raise ValueError("设定时间已过期，请修改为未来的时间")
    return target_datetime

def show_countdown(target: datetime):
    """动态显示倒计时"""
    try:
        while True:
            remaining = target - datetime.now()
            if remaining.total_seconds() <= 0:
                print("\n时间到！执行 main.py...")
                subprocess.run(["python", "main.py"], check=True)
                break

            hours, rem = divmod(int(remaining.total_seconds()), 3600)
            mins, secs = divmod(rem, 60)
            countdown = f"{hours:02}:{mins:02}:{secs:02}"
            print(f"\r倒计时: {countdown}", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n用户手动中断")

def main():
    try:
        config = load_config()
        validate_required_fields(config)
        target_time = parse_schedule_time(config["schedule_time"])
        print(f"任务计划执行时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        show_countdown(target_time)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        if isinstance(e, FileNotFoundError):
            print(f"请打开 {CONFIG_PATH} 填写配置后重新运行")

if __name__ == "__main__":
    main()