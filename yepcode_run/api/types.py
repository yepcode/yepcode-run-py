from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
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
    url: str
    secret: Optional[str] = None


@dataclass
class ProcessSettings:
    dependencies: Dict[str, Any]


@dataclass
class Process:
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    readme: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None
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
class ExecutionError:
    message: Optional[str] = None


@dataclass
class TimelineEvent:
    status: ExecutionStatus
    timestamp: str
    explanation: Optional[str] = None


@dataclass
class Execution:
    execution_id: str
    logs: List[Log]
    process_id: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    return_value: Optional[Any] = None
    error: Optional[str] = None
    timeline: Optional[List[TimelineEvent]] = None
    parameters: Optional[Dict[str, Any]] = None
    comment: Optional[str] = None


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
class DependenciesConfig:
    scoped_to_process: Optional[bool] = None
    auto_detect: Optional[bool] = None


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
class ProcessFormsConfig:
    enabled: Optional[bool] = None


@dataclass
class ProcessManifest:
    dependencies: Optional[Dict[str, str]] = None


@dataclass
class ProcessManifestInput:
    dependencies: Optional[Dict[str, str]] = None


@dataclass
class ProcessPublicationConfig:
    enabled: Optional[bool] = None
    token: Optional[str] = None


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
