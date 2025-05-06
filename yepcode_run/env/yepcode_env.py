from typing import List, Optional, Dict
from dataclasses import dataclass

from ..api.api_manager import YepCodeApiManager
from ..api.yepcode_api import YepCodeApi
from ..api.types import YepCodeApiConfig, TeamVariable


@dataclass
class EnvVar:
    key: str
    value: str


class YepCodeEnv:
    def __init__(self, config: YepCodeApiConfig = None):
        """
        Initialize YepCodeEnv with optional configuration.

        Args:
            config: YepCodeApiConfig instance for API configuration
        """
        if config is None:
            config = YepCodeApiConfig()
        self._yepcode_api = YepCodeApiManager.get_instance(config)

    def get_client_id(self) -> str:
        return self._yepcode_api.get_client_id()

    def get_team_id(self) -> str:
        return self._yepcode_api.get_team_id()

    def _get_variable(self, key: str) -> Optional[TeamVariable]:
        """
        Get a specific environment variable by key.

        Args:
            key: The environment variable key to look up

        Returns:
            TeamVariable if found, None otherwise
        """
        variables = self._get_variables()
        return next((v for v in variables if v.key == key), None)

    def _get_variables(self) -> List[TeamVariable]:
        """
        Get all environment variables.

        Returns:
            List of TeamVariable objects
        """
        page = 0
        limit = 100
        all_variables: List[TeamVariable] = []

        while True:
            response = self._yepcode_api.get_variables({"page": page, "limit": limit})

            variables = response.get("data", [])
            if variables:
                all_variables.extend(variables)

            if not response.get("hasNextPage"):
                break

            page += 1

        # Sort variables by key and extract required fields
        return sorted(
            [
                TeamVariable(
                    id=var["id"],
                    key=var["key"],
                    value=var["value"],
                    is_sensitive=var["isSensitive"],
                )
                for var in all_variables
            ],
            key=lambda x: x.key,
        )

    def get_env_vars(self) -> List[EnvVar]:
        """
        Get all environment variables as EnvVar objects.

        Returns:
            List of EnvVar objects containing key-value pairs
        """
        variables = self._get_variables()
        return [EnvVar(key=var.key, value=var.value) for var in variables]

    def set_env_var(self, key: str, value: str, is_sensitive: bool = True) -> None:
        """
        Set an environment variable.

        Args:
            key: Environment variable key
            value: Environment variable value
            is_sensitive: Whether the variable contains sensitive data
        """
        existing_var = self._get_variable(key)

        if existing_var:
            self._yepcode_api.update_variable(
                existing_var.id, {"key": key, "value": value}
            )
        else:
            self._yepcode_api.create_variable(
                {"key": key, "value": value, "isSensitive": is_sensitive}
            )

    def del_env_var(self, key: str) -> None:
        """
        Delete an environment variable.

        Args:
            key: The key of the environment variable to delete
        """
        existing_var = self._get_variable(key)

        if existing_var:
            self._yepcode_api.delete_variable(existing_var.id)
