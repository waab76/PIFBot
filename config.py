from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PIFBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_name: str = "LatherBot"
    blacklist: dict[str, str] = {
        "blacklisted_user": "Blacklist reason",
    }
    log_path: str = "/var/log/LatherBot.log"
    monitored_subreddits: list[str] = ["WetShaving", "ircbst"]
    karma_subreddits: list[str] = ["WetShaving"]
    storage_backend: str = "local"
    storage_path: str = "/tmp/pifbot_storage/pifs.json"


settings = Settings()

bot_name = settings.bot_name
blacklist = settings.blacklist
log_path = settings.log_path
monitored_subreddits = settings.monitored_subreddits
karma_subreddits = settings.karma_subreddits
storage_backend = settings.storage_backend
storage_path = settings.storage_path
