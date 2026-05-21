import logging

# 統一在這裡設定全域的日誌格式 (這段程式碼只會在第一次被 import 時執行一次)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_logger(name: str) -> logging.Logger:
    """
    取得日誌記錄器 (Logger)
    使用方式：logger = get_logger(__name__)
    """
    return logging.getLogger(name)
