# Check app/core/config.py content

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PetPooja API"
    app_env: str = "dev"
    app_port: int = 8000

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/petpooja"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    llm_model: str = "gemini-3.1-flash-lite-preview"

    # Placeholder for Module 2 usage.
    retell_api_key: str = ""
    retell_webhook_secret: str = ""

    # Supabase config for hosted Postgres and optional direct client usage.
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Dataset paths used for menu context and bulk seed operations.
    dataset_menu_csv_path: str = "Menu_Items_Set2.csv"
    dataset_pos_csv_path: str = "POS_Transactions_Set2.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
