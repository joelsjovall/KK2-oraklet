from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "HuggingFaceTB/SmolLM2-135M-Instruct"
    max_new_tokens: int = 80


settings = Settings()
