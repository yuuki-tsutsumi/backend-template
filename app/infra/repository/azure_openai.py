from openai import AzureOpenAI

from app.config import settings


def create_azure_openai_client() -> AzureOpenAI:
    try:
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to create an Azure OpenAI client: {e}")
