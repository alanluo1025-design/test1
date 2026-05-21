"""調試工具模塊 - 用於開發時的日誌與內容保存"""

import os
import time
from core.logging.logger import get_logger
from core.config.settings import settings

logger = get_logger(__name__)


def write_debug_file(prefix: str, source: str, content: str) -> None:
    """
    將抓取的內容寫入本地檔案，方便除錯與驗證，並加上時間戳記避免覆蓋。
    
    Args:
        prefix: 檔名前綴（會自動清理非法字元）
        source: 內容來源說明（如 URL）
        content: 要保存的內容
    """
    if not settings.save_debug_files:
        return

    try:
        debug_dir = "debug_logs"
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = int(time.time())
        # 將 prefix 中非英數字的字元替換為底線，避免不合法的檔名
        safe_prefix = "".join([c if c.isalnum() else "_" for c in prefix])
        filename = os.path.join(debug_dir, f"{safe_prefix}_{timestamp}.txt")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"來源：{source}\n")
            f.write(f"字數：{len(content)}\n")
            f.write("=" * 40 + "\n\n")
            f.write(content)
        logger.info(f"📁 已將內容寫入 {filename}，約 {len(content)} 字，以供除錯使用。")
    except Exception as e:
        logger.error(f"❌ 寫入除錯檔案時發生錯誤：{e}")
