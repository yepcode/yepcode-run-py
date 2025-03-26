import base64
import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import requests
from urllib.parse import urljoin

from .types import (
    YepCodeApiConfig,
    Process,
    Execution,
    ExecutionStatus,
    Schedule,
    TeamVariable,
)


class YepCodeApiError(Exception):
    def __init__(self, message: str, status: int):
        super().__init__(message)
        self.status = status
        self.name = "YepCodeApiError"


class YepCodeApi:
    def __init__(self, config: YepCodeApiConfig = None):
        config = config or YepCodeApiConfig()
        config_dict = (
            {k: v for k, v in config.__dict__.items() if v is not None}
            if config
            else {}
        )
        final_config = {
            "api_host": "https://cloud.yepcode.io",
            "timeout": 60000,
            **config_dict,
        }
        if not final_config.get("auth_url"):
            final_config["auth_url"] = (
                f"{final_config['api_host']}/auth/realms/yepcode/protocol/openid-connect/token"
            )

        if (
            not final_config.get("access_token")
            and not final_config.get("api_token")
            and (
                not final_config.get("client_id")
                or not final_config.get("client_secret")
            )
        ):
            raise ValueError(
                "Invalid configuration. Please provide either: access_token, api_token or client_id and client_secret."
            )

        if final_config.get("api_token"):
            try:
                decoded_token = base64.b64decode(final_config["api_token"]).decode()
                token_data = json.loads(decoded_token)
                if not token_data.get("clientId") or not token_data.get("clientSecret"):
                    raise ValueError()
                final_config["client_id"] = token_data["clientId"]
                final_config["client_secret"] = token_data["clientSecret"]
            except Exception as e:
                raise ValueError(
                    f"Invalid apiToken format: {final_config['api_token']}"
                )

        self.api_host = final_config.get("api_host")
        self.client_id = final_config.get("client_id")
        self.client_secret = final_config.get("client_secret")
        self.auth_url = final_config.get("auth_url")
        self.team_id = final_config.get("team_id")
        self.access_token = final_config.get("access_token")
        self.timeout = final_config.get("timeout")
        self._init_team_id_by_access_token()

    def _init_team_id_by_access_token(self) -> None:
        if not self.access_token:
            return

        payload = self.access_token.split(".")[1]
        # Add padding if necessary
        payload += "=" * ((4 - len(payload) % 4) % 4)
        decoded_payload = json.loads(base64.b64decode(payload).decode())

        if groups := decoded_payload.get("groups"):
            self.team_id = next((group for group in groups if group != "sandbox"), None)

        if not self.team_id:
            raise ValueError("No teamId found in the access token")

    def _get_base_url(self) -> str:
        return f"{self.api_host}/api/{self.team_id}/rest"

    def _get_access_token(self) -> str:
        try:
            auth_str = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            response = requests.post(
                self.auth_url,
                headers={
                    "Authorization": f"Basic {auth_str}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data="grant_type=client_credentials",
                timeout=self.timeout,
            )

            if not response.ok:
                raise ValueError(f"HTTP error! status: {response.status_code}")

            data = response.json()
            self.access_token = data["access_token"]
            if not self.access_token:
                raise ValueError("No access token received from server")

            self._init_team_id_by_access_token()
            return self.access_token

        except Exception as error:
            raise ValueError(f"Authentication failed: {str(error)}")

    def _request(
        self, method: str, endpoint: str, options: Dict[str, Any] = None
    ) -> Any:
        if options is None:
            options = {}

        if not self.access_token:
            self._get_access_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            **(options.get("headers", {})),
        }

        endpoint = endpoint.lstrip("/")
        url = urljoin(f"{self._get_base_url()}/", endpoint)
        request_kwargs = {"headers": headers, "timeout": self.timeout / 1000}

        if data := options.get("data"):
            request_kwargs["json"] = data

        if params := options.get("params"):
            request_kwargs["params"] = {
                k: str(v) for k, v in params.items() if v is not None
            }

        response = requests.request(method, url, **request_kwargs)

        if response.status_code == 401:
            self._get_access_token()
            return self._request(method, endpoint, options)

        if not response.ok:
            try:
                error_response = response.json()
                message = error_response.get("message", response.reason)
            except ValueError:
                message = response.reason

            raise YepCodeApiError(
                f"HTTP error {response.status_code} in endpoint {method} {endpoint}: {message}",
                response.status_code,
            )

        try:
            return response.json()
        except ValueError:
            return response.text

    def create_process(self, data: Dict[str, Any]) -> Process:
        return self._request("POST", "/processes", {"data": data})

    def get_process(self, id: str) -> Process:
        return self._request("GET", f"/processes/{id}")

    def update_process(self, process_identifier: str, data: Dict[str, Any]) -> Process:
        return self._request(
            "PATCH", f"/processes/{process_identifier}", {"data": data}
        )

    def delete_process(self, process_identifier: str) -> None:
        self._request("DELETE", f"/processes/{process_identifier}")

    def get_processes(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return self._request("GET", "/processes", {"params": params or {}})

    def execute_process_async(
        self,
        process_id_or_slug: str,
        parameters: Dict[str, Any] = None,
        options: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        headers = {}
        if options and options.get("initiatedBy"):
            headers["Yep-Initiated-By"] = options["initiatedBy"]

        data = {
            "parameters": json.dumps(parameters or {}),
            "tag": options.get("tag") if options else None,
            "comment": options.get("comment") if options else None,
            "settings": options.get("settings") if options else None,
        }

        return self._request(
            "POST",
            f"/processes/{process_id_or_slug}/execute",
            {"data": data, "headers": headers},
        )

    def execute_process_sync(
        self,
        process_id_or_slug: str,
        parameters: Dict[str, Any] = None,
        options: Dict[str, Any] = None,
    ) -> Any:
        headers = {}
        if options and options.get("initiatedBy"):
            headers["Yep-Initiated-By"] = options["initiatedBy"]

        data = {
            "parameters": json.dumps(parameters or {}),
            "tag": options.get("tag") if options else None,
            "comment": options.get("comment") if options else None,
            "settings": options.get("settings") if options else None,
        }

        return self._request(
            "POST",
            f"/processes/{process_id_or_slug}/execute-sync",
            {"data": data, "headers": headers},
        )

    @staticmethod
    def _sanitize_date_param(date: Union[datetime, str, None]) -> Optional[str]:
        if not date:
            return None
        if isinstance(date, datetime):
            return date.isoformat().split(".")[0]
        if isinstance(date, str) and not date.match(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
        ):
            raise ValueError(
                "Invalid date format. It must be a valid ISO 8601 date (ie: 2025-01-01T00:00:00)"
            )
        return date

    def get_executions(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if params:
            sanitized_params = {
                **params,
                "from": self._sanitize_date_param(params.get("from")),
                "to": self._sanitize_date_param(params.get("to")),
            }
        else:
            sanitized_params = {}
        return self._request("GET", "/executions", {"params": sanitized_params})

    def get_execution(self, id: str) -> Execution:
        return self._request("GET", f"/executions/{id}")

    def get_execution_logs(
        self, id: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        return self._request("GET", f"/executions/{id}/logs", {"params": params or {}})

    def rerun_execution(self, id: str) -> str:
        response = self._request("POST", f"/executions/{id}/rerun")
        return response["executionId"]

    def kill_execution(self, id: str) -> None:
        self._request("PUT", f"/executions/{id}/kill")

    def get_schedules(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return self._request("GET", "/schedules", {"params": params or {}})

    def get_schedule(self, id: str) -> Schedule:
        return self._request("GET", f"/schedules/{id}")

    def delete_schedule(self, id: str) -> None:
        self._request("DELETE", f"/schedules/{id}")

    def pause_schedule(self, id: str) -> None:
        self._request("PUT", f"/schedules/{id}/pause")

    def resume_schedule(self, id: str) -> None:
        self._request("PUT", f"/schedules/{id}/resume")

    def get_variables(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return self._request("GET", "/variables", {"params": params or {}})

    def create_variable(self, data: Dict[str, Any]) -> TeamVariable:
        return self._request("POST", "/variables", {"data": data})

    def update_variable(self, id: str, data: Dict[str, Any]) -> TeamVariable:
        return self._request("PATCH", f"/variables/{id}", {"data": data})

    def delete_variable(self, id: str) -> None:
        self._request("DELETE", f"/variables/{id}")
