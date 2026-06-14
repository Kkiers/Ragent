# 读 ENV：provider、model、key、base_url、timeout
#
# 统一只读取：项目根目录的 `.env`（本项目只保留一个 .env）。

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CONFIG_DIR.parents[3]  # .../Ragent


def _llm_env_files() -> tuple[str, ...]:
    files: list[str] = []
    root_env = _PROJECT_ROOT / ".env"
    if root_env.is_file():
        files.append(str(root_env))
    if not files:
        files.append(".env")
    return tuple(files)


class LLMSettings(BaseSettings):
    """
    统一 LLM 配置入口：
    - provider: openai / deepseek / ollama
    - model: 模型名
    - api_key / base_url: 按 provider 读取
    - timeout / temperature / max_retries: 工程参数
    """

    model_config = SettingsConfigDict(
        env_file=_llm_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 基础配置声明类型（默认沿用 DeepSeek）
    provider: str = Field(default="deepseek", alias="LLM_PROVIDER")
    model: str = Field(default="deepseek-chat", alias="LLM_MODEL")
    temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    timeout: int = Field(default=60, alias="LLM_TIMEOUT")
    max_retries: int = Field(default=2, alias="LLM_MAX_RETRIES")
    max_tokens: int = Field(default=2048, alias="LLM_MAX_TOKENS")

    # openai
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")

    #deepseek
    deepseek_api_key: str | None = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str | None = Field(default=None, alias="DEEPSEEK_BASE_URL")
    
    #Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")


def load_llm_settings() -> LLMSettings:
    return LLMSettings()



#test
# if __name__ == "__main__":
#     settings = load_llm_settings()
#     settings.provider
#     settings.model
#     settings.deepseek_api_key