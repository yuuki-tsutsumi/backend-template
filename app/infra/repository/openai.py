from openai import OpenAI

from app.config import settings


def create_openai_client() -> OpenAI:
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to create an OpenAI client: {e}")
