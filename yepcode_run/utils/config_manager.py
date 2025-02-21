import os
import re
from typing import Dict, Any
from dotenv import load_dotenv
from ..api.types import YepCodeApiConfig


class ConfigManager:
    @staticmethod
    def read_yepcode_env_config() -> YepCodeApiConfig:
        # Load environment variables from .env file
        load_dotenv()

        # Filter and process YEPCODE_ environment variables
        env_config: Dict[str, Any] = {}
        for key, value in os.environ.items():
            if key.startswith("YEPCODE_") and value:
                config_key = key.lower().replace("yepcode_", "")
                env_config[config_key] = value

        # Create and return YepCodeApiConfig instance
        return YepCodeApiConfig(**env_config)
