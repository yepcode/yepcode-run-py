import hashlib
import json
from typing import Dict, ClassVar
from .yepcode_api import YepCodeApi
from .types import YepCodeApiConfig
from ..utils.config_manager import ConfigManager


class YepCodeApiManager:
    _instances: ClassVar[Dict[str, YepCodeApi]] = {}

    @staticmethod
    def _get_config_hash(config: YepCodeApiConfig) -> str:
        # Convert config to dictionary if it's a dataclass
        config_dict = config.__dict__ if hasattr(config, "__dict__") else config

        # Sort the config keys and create a new dictionary
        sorted_config = {
            key: config_dict[key]
            for key in sorted(config_dict.keys())
            if config_dict[key] is not None
        }

        # Convert to JSON string and create hash
        config_str = json.dumps(sorted_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    @classmethod
    def get_instance(cls, config: YepCodeApiConfig = None) -> YepCodeApi:
        if config is None:
            config = YepCodeApiConfig()

        # Merge environment config with provided config
        env_config = ConfigManager.read_yepcode_env_config()

        # Start with env_config dict
        merged_dict = env_config.__dict__.copy()

        # Only update with non-None values from config
        merged_dict.update({k: v for k, v in config.__dict__.items() if v is not None})

        merged_config = YepCodeApiConfig(**merged_dict)

        config_hash = cls._get_config_hash(merged_config)

        if config_hash not in cls._instances:
            cls._instances[config_hash] = YepCodeApi(merged_config)

        return cls._instances[config_hash]

    @classmethod
    def clear_instances(cls) -> None:
        cls._instances.clear()
