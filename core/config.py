import logging
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

# Setup minimal logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_consensus_engine")

class Settings(BaseSettings):
    project_name: str = "ELS JUDGE"
    database_url: str = "sqlite:///./consensus.db"
    
    # Optional LLM API keys. LiteLLM picks these up automatically if set in ENV,
    # but having them in settings is good practice to ensure they exist or log warnings.
    openai_api_key: str | None = None
    zhipuai_api_key: str | None = None
    zai_api_key: str | None = None
    
    # Models to use
    primary_model: str = "gpt-4o"
    secondary_model: str = "zai/glm-4.5-flash"
    tertiary_model: str = "gemini/gemini-flash-latest"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
