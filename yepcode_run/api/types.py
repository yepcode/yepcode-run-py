from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class ProgrammingLanguage(Enum):
    JAVASCRIPT = "JAVASCRIPT"
    PYTHON = "PYTHON"


class ExecutionStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    KILLED = "KILLED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


@dataclass
class YepCodeApiConfig:
    auth_url: Optional[str] = None
    api_host: Optional[str] = None
    timeout: Optional[int] = None
    access_token: Optional[str] = None
    api_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    team_id: Optional[str] = None


@dataclass
class ProcessWebhook:
    enabled: Optional[bool] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class ProcessFormsConfig:
    enabled: Optional[bool] = None


@dataclass
class ProcessPublicationConfig:
    enabled: Optional[bool] = None
    token: Optional[str] = None


@dataclass
class DependenciesConfig:
    scoped_to_process: Optional[bool] = None
    auto_detect: Optional[bool] = None


@dataclass
class ProcessSettings:
    forms_config: Optional[ProcessFormsConfig] = None
    public_config: Optional[ProcessPublicationConfig] = None
    dependencies: Optional[DependenciesConfig] = None


@dataclass
class ProcessManifest:
    dependencies: Optional[Dict[str, str]] = None


@dataclass
class Process:
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    readme: Optional[str] = None
    manifest: Optional[ProcessManifest] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    parameters_schema: Optional[Dict[str, Dict[str, Any]]] = None
    programming_language: Optional[ProgrammingLanguage] = None
    source_code: Optional[str] = None
    webhook: Optional[ProcessWebhook] = None
    settings: Optional[ProcessSettings] = None
    tags: Optional[List[str]] = None


@dataclass
class Log:
    timestamp: str
    level: str
    message: str


@dataclass
class TimelineEvent:
    status: ExecutionStatus
    timestamp: str
    explanation: Optional[str] = None


@dataclass
class ExecutionTimeline:
    explanation: Optional[str] = None
    events: Optional[List[TimelineEvent]] = None


@dataclass
class ExecutionSettings:
    timeout: Optional[int] = None
    agent_pool_slug: Optional[str] = None


@dataclass
class Execution:
    id: str
    process_id: str
    status: ExecutionStatus
    scheduled_id: Optional[str] = None
    timeline: Optional[ExecutionTimeline] = None
    parameters: Optional[Dict[str, Dict[str, Any]]] = None
    comment: Optional[str] = None
    return_value: Optional[Any] = None
    settings: Optional[ExecutionSettings] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ExecutionId:
    execution_id: str


@dataclass
class CreateProcessInput:
    name: str
    description: Optional[str] = None
    readme: Optional[str] = None
    manifest: Optional["ProcessManifestInput"] = None
    settings: Optional["SettingsInput"] = None
    script: Optional["CreateScriptInput"] = None
    tags: Optional[List[str]] = None


@dataclass
class CreateScriptInput:
    programming_language: Optional[str] = None
    source_code: Optional[str] = None
    parameters_schema: Optional[str] = None


@dataclass
class CreateTeamVariableInput:
    key: str
    value: Optional[str] = None
    is_sensitive: Optional[bool] = None


@dataclass
class DependenciesConfigInput:
    scoped_to_process: Optional[bool] = None
    auto_detect: Optional[bool] = None


@dataclass
class ExecuteProcessInput:
    parameters: Optional[str] = None
    tag: Optional[str] = None
    comment: Optional[str] = None
    settings: Optional["ExecuteProcessSettingsInput"] = None


@dataclass
class ExecuteProcessSettingsInput:
    agent_pool_slug: Optional[str] = None
    callback_url: Optional[str] = None


@dataclass
class FormsConfigInput:
    enabled: Optional[bool] = None


@dataclass
class ProcessManifestInput:
    dependencies: Optional[Dict[str, str]] = None


@dataclass
class PublicationConfigInput:
    enabled: Optional[bool] = None
    token: Optional[str] = None


@dataclass
class Schedule:
    id: str
    process_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    comment: Optional[str] = None
    parameters: Optional[Dict[str, Dict[str, Any]]] = None
    paused: Optional[bool] = None
    type: Optional[str] = None  # "PERIODIC" | "ONE_TIME"
    cron: Optional[str] = None
    date_time: Optional[datetime] = None
    settings: Optional["ScheduleSettings"] = None


@dataclass
class ScheduleSettings:
    allow_concurrent_executions: Optional[bool] = None
    agent_pool_slugs: Optional[List[str]] = None


@dataclass
class ScheduledProcessInput:
    cron: Optional[str] = None
    date_time: Optional[datetime] = None
    allow_concurrent_executions: Optional[bool] = None
    input: Optional[ExecuteProcessInput] = None


@dataclass
class TeamVariable:
    id: str
    key: str
    value: Optional[str] = None
    is_sensitive: Optional[bool] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class UpdateTeamVariableInput:
    key: str
    value: Optional[str] = None


@dataclass
class UpdateProcessInput:
    name: str
    slug: str
    description: Optional[str] = None
    readme: Optional[str] = None
    script: Optional["UpdateScriptInput"] = None
    webhook: Optional["WebhookInput"] = None
    settings: Optional["SettingsInput"] = None
    manifest: Optional[ProcessManifestInput] = None
    tags: Optional[List[str]] = None


@dataclass
class UpdateScriptInput:
    source_code: Optional[str] = None
    parameters_schema: Optional[str] = None


@dataclass
class WebhookInput:
    enabled: Optional[bool] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class SettingsInput:
    forms_config: Optional[FormsConfigInput] = None
    public_config: Optional[PublicationConfigInput] = None
    dependencies: Optional[DependenciesConfigInput] = None


# Pagination result types
@dataclass
class PaginatedResult:
    has_next_page: Optional[bool] = None
    page: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None


@dataclass
class ProcessesPaginatedResult(PaginatedResult):
    data: Optional[List[Process]] = None


@dataclass
class ExecutionsPaginatedResult(PaginatedResult):
    data: Optional[List[Execution]] = None


@dataclass
class ExecutionLogsPaginatedResult(PaginatedResult):
    data: Optional[List[Log]] = None


@dataclass
class SchedulesPaginatedResult(PaginatedResult):
    data: Optional[List[Schedule]] = None


@dataclass
class TeamVariablesPaginatedResult(PaginatedResult):
    data: Optional[List[TeamVariable]] = None


# Versioned process types
@dataclass
class VersionedProcess:
    id: str
    programming_language: ProgrammingLanguage
    source_code: str
    parameters_schema: str
    readme: str
    comment: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class PublishProcessInput:
    tag: str
    comment: Optional[str] = None


@dataclass
class VersionedProcessesPaginatedResult(PaginatedResult):
    data: Optional[List[VersionedProcess]] = None


@dataclass
class VersionedProcessAlias:
    id: str
    name: str
    version_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class VersionedProcessAliasInput:
    name: str
    version_id: str


@dataclass
class VersionedProcessAliasesPaginatedResult(PaginatedResult):
    data: Optional[List[VersionedProcessAlias]] = None


# Module types
@dataclass
class Module:
    id: str
    name: str
    programming_language: Optional[ProgrammingLanguage] = None
    source_code: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateModuleScriptInput:
    programming_language: Optional[str] = None
    source_code: Optional[str] = None


@dataclass
class CreateModuleInput:
    name: str
    script: Optional[CreateModuleScriptInput] = None


@dataclass
class UpdateModuleInput:
    name: Optional[str] = None
    script: Optional[CreateModuleScriptInput] = None


@dataclass
class ModulesPaginatedResult(PaginatedResult):
    data: Optional[List[Module]] = None


@dataclass
class VersionedModule:
    id: str
    programming_language: ProgrammingLanguage
    source_code: str
    comment: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class PublishModuleInput:
    tag: str
    comment: Optional[str] = None


@dataclass
class VersionedModulesPaginatedResult(PaginatedResult):
    data: Optional[List[VersionedModule]] = None


@dataclass
class VersionedModuleAlias:
    id: str
    name: str
    version_id: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class VersionedModuleAliasInput:
    name: str
    version_id: str


@dataclass
class VersionedModuleAliasesPaginatedResult(PaginatedResult):
    data: Optional[List[VersionedModuleAlias]] = None


# Storage types
@dataclass
class StorageObject:
    name: str
    size: int
    md5_hash: str
    content_type: str
    created_at: str
    updated_at: str
    link: str

    @staticmethod
    def from_dict(data: dict) -> "StorageObject":
        return StorageObject(
            name=data["name"],
            size=data["size"],
            md5_hash=data.get("md5Hash", data.get("md5_hash")),
            content_type=data.get("contentType", data.get("content_type")),
            created_at=data.get("createdAt", data.get("created_at")),
            updated_at=data.get("updatedAt", data.get("updated_at")),
            link=str(data.get("link")),
        )


@dataclass
class CreateStorageObjectInput:
    name: str
    file: Any
