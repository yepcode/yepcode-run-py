import base64
import json
from typing import Optional, Dict, Any, List, Union, Tuple
from datetime import datetime
import requests
from urllib.parse import urljoin
import mimetypes

from .types import (
    YepCodeApiConfig,
    Process,
    Execution,
    ExecutionId,
    ExecutionsPaginatedResult,
    ExecutionLogsPaginatedResult,
    ProcessesPaginatedResult,
    Schedule,
    SchedulesPaginatedResult,
    TeamVariable,
    TeamVariablesPaginatedResult,
    VersionedProcess,
    VersionedProcessesPaginatedResult,
    VersionedProcessAlias,
    VersionedProcessAliasesPaginatedResult,
    Module,
    ModulesPaginatedResult,
    VersionedModule,
    VersionedModulesPaginatedResult,
    VersionedModuleAlias,
    VersionedModuleAliasesPaginatedResult,
    CreateProcessInput,
    UpdateProcessInput,
    CreateTeamVariableInput,
    UpdateTeamVariableInput,
    CreateModuleInput,
    UpdateModuleInput,
    PublishProcessInput,
    PublishModuleInput,
    VersionedProcessAliasInput,
    VersionedModuleAliasInput,
    ScheduledProcessInput,
    CreateStorageObjectInput,
    StorageObject,
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
                api_token = final_config["api_token"]
                if api_token.startswith("sk-"):
                    decoded_token = base64.b64decode(api_token[3:]).decode()
                    client_id, client_secret = decoded_token.split(":")
                    if not client_id or not client_secret:
                        raise ValueError()
                    final_config["client_id"] = client_id
                    final_config["client_secret"] = client_secret
                else:
                    # Legacy apiToken format
                    decoded_token = base64.b64decode(api_token).decode()
                    token_data = json.loads(decoded_token)
                    if not token_data.get("clientId") or not token_data.get(
                        "clientSecret"
                    ):
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
        if not self.client_id and self.access_token:
            self.client_id = self._client_id_from_access_token()
        if not self.team_id and self.client_id:
            self.team_id = self._team_id_from_client_id()

    def get_client_id(self) -> str:
        if not self.client_id:
            raise ValueError("Client ID is not set")
        return self.client_id

    def get_team_id(self) -> str:
        if not self.team_id:
            raise ValueError("Team ID is not set")
        return self.team_id

    def _client_id_from_access_token(self) -> str:
        if not self.access_token:
            raise ValueError("Access token is not set")
        try:
            payload = self.access_token.split(".")[1]
            payload += "=" * ((4 - len(payload) % 4) % 4)
            decoded_payload = json.loads(base64.b64decode(payload).decode())
            return decoded_payload["client_id"]
        except Exception as e:
            raise ValueError(f"Failed to extract client_id from access token: {e}")

    def _team_id_from_client_id(self) -> str:
        if not self.client_id:
            raise ValueError("Client ID is not set")
        import re

        match = re.match(r"^sa-(.*)-[a-z0-9]{8}$", self.client_id)
        if not match:
            raise ValueError(
                "Client ID is not valid. It must be in the format sa-<teamId>-<8randomCharsOrDigits>"
            )
        return match.group(1)

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

            return self.access_token

        except Exception as error:
            raise ValueError(f"Authentication failed: {str(error)}")

    def _request(
        self, method: str, endpoint: str, options: Optional[Dict[str, Any]] = None
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

    def create_process(self, data: CreateProcessInput) -> Process:
        return self._request("POST", "/processes", {"data": data})

    def get_process(self, id: str) -> Process:
        return self._request("GET", f"/processes/{id}")

    def update_process(
        self, process_identifier: str, data: UpdateProcessInput
    ) -> Process:
        return self._request(
            "PATCH", f"/processes/{process_identifier}", {"data": data}
        )

    def delete_process(self, process_identifier: str) -> None:
        self._request("DELETE", f"/processes/{process_identifier}")

    def get_process_versions(
        self, process_id: str, params: Optional[Dict[str, Any]] = None
    ) -> VersionedProcessesPaginatedResult:
        return self._request(
            "GET", f"/processes/{process_id}/versions", {"params": params or {}}
        )

    def publish_process_version(
        self, process_id: str, data: PublishProcessInput
    ) -> VersionedProcess:
        return self._request(
            "POST", f"/processes/{process_id}/versions", {"data": data}
        )

    def get_process_version_aliases(
        self, process_id: str, params: Optional[Dict[str, Any]] = None
    ) -> VersionedProcessAliasesPaginatedResult:
        return self._request(
            "GET", f"/processes/{process_id}/aliases", {"params": params or {}}
        )

    def create_process_version_alias(
        self, process_id: str, data: VersionedProcessAliasInput
    ) -> VersionedProcessAlias:
        return self._request("POST", f"/processes/{process_id}/aliases", {"data": data})

    def get_processes(
        self, params: Optional[Dict[str, Any]] = None
    ) -> ProcessesPaginatedResult:
        return self._request("GET", "/processes", {"params": params or {}})

    def execute_process_async(
        self,
        process_id_or_slug: str,
        parameters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ExecutionId:
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
        parameters: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
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

    def create_schedule(
        self, process_id_or_slug: str, data: ScheduledProcessInput
    ) -> Schedule:
        return self._request(
            "POST", f"/processes/{process_id_or_slug}/schedule", {"data": data}
        )

    def get_executions(
        self, params: Optional[Dict[str, Any]] = None
    ) -> ExecutionsPaginatedResult:
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
        self, id: str, params: Optional[Dict[str, Any]] = None
    ) -> ExecutionLogsPaginatedResult:
        return self._request("GET", f"/executions/{id}/logs", {"params": params or {}})

    def rerun_execution(self, id: str) -> str:
        response = self._request("POST", f"/executions/{id}/rerun")
        return response["executionId"]

    def kill_execution(self, id: str) -> None:
        self._request("PUT", f"/executions/{id}/kill")

    def get_schedules(
        self, params: Optional[Dict[str, Any]] = None
    ) -> SchedulesPaginatedResult:
        return self._request("GET", "/schedules", {"params": params or {}})

    def get_schedule(self, id: str) -> Schedule:
        return self._request("GET", f"/schedules/{id}")

    def delete_schedule(self, id: str) -> None:
        self._request("DELETE", f"/schedules/{id}")

    def pause_schedule(self, id: str) -> None:
        self._request("PUT", f"/schedules/{id}/pause")

    def resume_schedule(self, id: str) -> None:
        self._request("PUT", f"/schedules/{id}/resume")

    def get_variables(
        self, params: Optional[Dict[str, Any]] = None
    ) -> TeamVariablesPaginatedResult:
        return self._request("GET", "/variables", {"params": params or {}})

    def create_variable(self, data: CreateTeamVariableInput) -> TeamVariable:
        return self._request("POST", "/variables", {"data": data})

    def update_variable(self, id: str, data: UpdateTeamVariableInput) -> TeamVariable:
        return self._request("PATCH", f"/variables/{id}", {"data": data})

    def delete_variable(self, id: str) -> None:
        self._request("DELETE", f"/variables/{id}")

    def get_modules(
        self, params: Optional[Dict[str, Any]] = None
    ) -> ModulesPaginatedResult:
        return self._request("GET", "/modules", {"params": params or {}})

    def create_module(self, data: CreateModuleInput) -> Module:
        return self._request("POST", "/modules", {"data": data})

    def get_module(self, id: str) -> Module:
        return self._request("GET", f"/modules/{id}")

    def update_module(self, id: str, data: UpdateModuleInput) -> Module:
        return self._request("PATCH", f"/modules/{id}", {"data": data})

    def delete_module(self, id: str) -> None:
        self._request("DELETE", f"/modules/{id}")

    def get_module_versions(
        self, module_id: str, params: Optional[Dict[str, Any]] = None
    ) -> VersionedModulesPaginatedResult:
        return self._request(
            "GET", f"/modules/{module_id}/versions", {"params": params or {}}
        )

    def publish_module_version(
        self, module_id: str, data: PublishModuleInput
    ) -> VersionedModule:
        return self._request("POST", f"/modules/{module_id}/versions", {"data": data})

    def get_module_version_aliases(
        self, module_id: str, params: Optional[Dict[str, Any]] = None
    ) -> VersionedModuleAliasesPaginatedResult:
        return self._request(
            "GET", f"/modules/{module_id}/aliases", {"params": params or {}}
        )

    def create_module_version_alias(
        self, module_id: str, data: VersionedModuleAliasInput
    ) -> VersionedModuleAlias:
        return self._request("POST", f"/modules/{module_id}/aliases", {"data": data})

    def get_objects(self) -> List[StorageObject]:
        response = self._request("GET", "/storage/objects")
        return [StorageObject.from_dict(obj) for obj in response]

    def get_object(self, name: str) -> requests.Response:
        if not self.access_token:
            self._get_access_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        endpoint = f"/storage/objects/{name}"
        url = urljoin(f"{self._get_base_url()}/", endpoint.lstrip("/"))
        response = requests.get(url, headers=headers, stream=True, timeout=self.timeout / 1000)
        response.raise_for_status()
        return response

    def create_object(self, data: CreateStorageObjectInput) -> StorageObject:
        if not data.file:
            raise ValueError("File or stream is required")
        if not self.access_token:
            self._get_access_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        endpoint = f"/storage/objects?name={requests.utils.quote(data.name)}"
        url = urljoin(f"{self._get_base_url()}/", endpoint.lstrip("/"))
        # Detect content type
        content_type, _ = mimetypes.guess_type(data.name)
        files = {"file": (data.name, data.file, content_type or "application/octet-stream")}
        response = requests.post(url, headers=headers, files=files, timeout=self.timeout / 1000)
        if not response.ok:
            try:
                error_response = response.json()
                message = error_response.get("message", response.reason)
            except ValueError:
                message = response.reason
            raise YepCodeApiError(
                f"HTTP error {response.status_code} in endpoint POST {endpoint}: {message}",
                response.status_code,
            )
        return StorageObject.from_dict(response.json())

    def delete_object(self, name: str) -> None:
        if not self.access_token:
            self._get_access_token()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        endpoint = f"/storage/objects/{requests.utils.quote(name)}"
        url = urljoin(f"{self._get_base_url()}/", endpoint.lstrip("/"))
        response = requests.delete(url, headers=headers, timeout=self.timeout / 1000)
        if not response.ok:
            try:
                error_response = response.json()
                message = error_response.get("message", response.reason)
            except ValueError:
                message = response.reason
            raise YepCodeApiError(
                f"HTTP error {response.status_code} in endpoint DELETE {endpoint}: {message}",
                response.status_code,
            )
        return None
