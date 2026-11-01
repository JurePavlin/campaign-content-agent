"""Settings from the environment and the project's .env file."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# The project's .env wins over machine-wide variables such as LANGSMITH_PROJECT=default.
# LangSmith reads os.environ directly, so this must run before any traced code.
load_dotenv(override=True)


class Settings(BaseSettings):
    # One Microsoft Foundry resource and key, two endpoints: Claude uses Anthropic's
    # Messages API, the OpenAI models use the OpenAI-compatible v1 API.
    foundry_api_key: str = ""
    foundry_anthropic_endpoint: str = ""
    foundry_openai_endpoint: str = ""
    writer_deployment: str = "claude-haiku-5-5"
    checker_deployment: str = "gpt-6-luna"
    embedding_deployment: str = "text-embedding-3-large"
    embedding_dimensions: int = 1536  # pgvector's HNSW index takes at most 2,000
    database_url: str = "postgresql://agent:agent@localhost:5432/campaign_agent"


settings = Settings()
