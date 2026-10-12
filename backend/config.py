import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str = os.getenv("COZY_ENV", "development")
    data_dir: str = os.getenv("COZY_DATA_DIR", ".cozy-data")
    public_app_origin: str = os.getenv(
        "COZY_PUBLIC_APP_ORIGIN",
        "https://solandrade.github.io/cozy-publishing-studio",
    )

    def validate_for_production(self) -> None:
        if self.environment == "production" and self.public_app_origin.startswith("http://"):
            raise ValueError("Production app origin must use HTTPS")
