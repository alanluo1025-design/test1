"""
core.utils - 系統通用工具模塊

包含調試工具與內容處理工具，供整個系統使用。
"""

from .debug import write_debug_file
from .processor import process_and_store_long_content

__all__ = [
    "write_debug_file",
    "process_and_store_long_content",
]
