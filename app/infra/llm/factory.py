# provider 工厂：按需懒加载，避免未安装的 langchain-* 包在 import 阶段报错
from app.infra.llm.config import LLMSettings
from app.infra.llm.providers.base import BaseLLMProvider


def create_llm_provider(settings: LLMSettings) -> BaseLLMProvider:
    provider = settings.provider.lower().strip()
    if provider == "openai":
        from app.infra.llm.providers.openai_provider import OpenAIProvider

        return OpenAIProvider(settings)

    if provider == "deepseek":
        from app.infra.llm.providers.deepseek_provider import DeepSeekProvider

        return DeepSeekProvider(settings)

    if provider == "ollama":
        from app.infra.llm.providers.ollama_provider import OllamaProvider

        return OllamaProvider(settings)

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.provider}")
