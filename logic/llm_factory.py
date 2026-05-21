from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from core.logging.logger import get_logger
from core.config.settings import settings


logger = get_logger(__name__)

def get_llm(provider: Optional[str] = None, model_name: Optional[str] = None, temperature: float = 0.1):
    """
    動態生成並回傳 LLM 實例。
    若有傳入 provider/model_name 則優先使用；
    若未傳入，則退回讀取 .env 環境變數做為全域預設值。
    """
    actual_provider = (provider or settings.llm_provider).lower()
    
    if actual_provider == "gemini":
        actual_model = model_name or settings.gemini_model
        api_key = settings.google_api_key
        if not api_key:
            raise ValueError("啟動失敗：未設定 GOOGLE_API_KEY，請檢查 .env 檔案。")
            
        logger.info(f"🤖 [系統] 當前載入模型：Google Gemini ({actual_model})")
        return ChatGoogleGenerativeAI(
            model=actual_model,
            temperature=temperature,
            api_key=api_key
        )
        
    elif actual_provider == "nvidia":
        actual_model = model_name or settings.nvidia_model
        api_key = settings.nvidia_api_key
        if not api_key:
            raise ValueError("啟動失敗：未設定 NVIDIA_API_KEY，請檢查 .env 檔案。")
            
        logger.info(f"🟢 [系統] 當前載入模型：NVIDIA NIM ({actual_model})")
        return ChatNVIDIA(
            model=actual_model,
            temperature=temperature,
            max_tokens=4096,
            nvidia_api_key=api_key
        )

    elif actual_provider == "ollama":
        actual_model = model_name or settings.ollama_model
        base_url = settings.ollama_base_url
        logger.info(f"🦙 [系統] 當前載入模型：Ollama ({actual_model})")
        return ChatOllama(
            model=actual_model,
            base_url=base_url,
            temperature=temperature
        )
        
    else:
        raise ValueError(f"不支援的模型供應商: {actual_provider}")