from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    td_host: str
    td_user: str
    td_password: SecretStr
    td_logmech: str = "TD2"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def get_connection_url(self) -> str:
        return (
            f"teradatasql://{self.td_user}:{self.td_password.get_secret_value()}"
            f"@{self.td_host}/?logmech={self.td_logmech}"
        )


settings = Settings()  # type: ignore[call-arg]
