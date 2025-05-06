from dataclasses import dataclass
from typing import Optional
from enum import Enum


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
