"""
core.logging - 日誌系統模塊

統一管理應用的日誌配置和記錄器工廠。
"""

from .logger import get_logger

__all__ = ["get_logger"]
