"""Settings from the environment and the project's .env file."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# The project's .env wins over machine-wide variables such as LANGSMITH_PROJECT=default.
# LangSmith reads os.environ directly, so this must run before any traced code.
load_dotenv(override=True)


class Settings(BaseSettings):
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    writer_deployment: str = "gpt-5.4"
    checker_deployment: str = "gpt-5.4-mini"
    embedding_deployment: str = "text-embedding-3-small"
    database_url: str = "postgresql://agent:agent@localhost:5432/campaign_agent"


settings = Settings()
