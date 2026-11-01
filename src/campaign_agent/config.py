"""Settings from the environment and the project's .env file."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# The project's .env wins over machine-wide variables such as LANGSMITH_PROJECT=default.
# LangSmith reads os.environ directly, so this must run before any traced code.
load_dotenv(override=True)


class Settings(BaseSettings):
    # Claude on Foundry (Anthropic Messages API): the writer. The ANTHROPIC_FOUNDRY_*
    # names match the ones the Anthropic SDK's own Foundry client reads.
    anthropic_foundry_api_key: str = ""
    anthropic_foundry_base_url: str = ""
    writer_model: str = "claude-haiku-5-5"

    # OpenAI models on Foundry (OpenAI-compatible v1 API): the checker and embeddings.
    openai_foundry_api_key: str = ""
    openai_foundry_base_url: str = ""
    checker_model: str = "gpt-6-luna"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 1536  # pgvector's HNSW index takes at most 2,000

    database_url: str = "postgresql://agent:agent@localhost:5432/campaign_agent"


settings = Settings()
