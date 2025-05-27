import json
from datetime import datetime
from typing import Optional, Any, List, Dict, Callable
import time

from ..api.yepcode_api import YepCodeApi
from ..api.types import ExecutionStatus, Log, TimelineEvent


class Execution:
    def __init__(
        self,
        yepcode_api: YepCodeApi,
        execution_id: str,
        events: Dict[str, Callable] = None,
    ):
        self.yepcode_api = yepcode_api
        self.id = execution_id
        self.events = events or {}

        self.is_polling = True
        self.poll_attempts = 0

        self.logs: List[Log] = []
        self.process_id: Optional[str] = None
        self.status: Optional[ExecutionStatus] = None
        self.return_value: Any = None
        self.error: Optional[str] = None
        self.timeline: Optional[List[TimelineEvent]] = None
        self.parameters: Any = None
        self.comment: Optional[str] = None

        self.last_log_poll = 0
        self.LOG_POLL_INTERVAL = 2000  # Poll logs every 2 seconds

        self._poll()

    def init(self) -> None:
        pass  # No longer needed as _poll is called in __init__

    def _fetch_logs(self) -> List[Log]:
        page = 0
        limit = 100
        logs: List[Log] = []

        while True:
            response = self.yepcode_api.get_execution_logs(
                self.id, {"page": page, "limit": limit}
            )

            if log_entries := response.get("data"):
                logs.extend([Log(**log) for log in log_entries])

            if not response.get("hasNextPage"):
                break

            page += 1

        return sorted(logs, key=lambda x: datetime.fromisoformat(x.timestamp))

    def is_done(self) -> bool:
        return self._is_done(self.status)

    def wait_for_done(self) -> None:
        while not self.is_done():
            time.sleep(self._get_polling_interval())
            self._poll()

    def _poll_logs(self) -> None:
        current_logs = self._fetch_logs()
        for log in current_logs:
            if not self._log_already_processed(log):
                self.logs.append(log)
                if on_log := self.events.get("onLog"):
                    on_log(log)

    def _poll(self) -> None:
        self.is_polling = True
        try:
            execution_data = self.yepcode_api.get_execution(self.id)

            self.process_id = execution_data.get("processId")
            self.status = ExecutionStatus(execution_data.get("status"))
            self.timeline = [
                TimelineEvent(**event)
                for event in (execution_data.get("timeline", {}).get("events") or [])
            ]
            self.parameters = execution_data.get("parameters")
            self.comment = execution_data.get("comment")

            now = time.time() * 1000
            if now - self.last_log_poll >= self.LOG_POLL_INTERVAL or self._is_done(
                self.status
            ):
                self._poll_logs()
                self.last_log_poll = now

            if not self._is_done(self.status):
                self.poll_attempts += 1
                time.sleep(self._get_polling_interval())
                self._poll()
                return

            if return_value := execution_data.get("returnValue"):
                try:
                    self.return_value = json.loads(return_value)
                except json.JSONDecodeError:
                    self.return_value = return_value

            if self._is_failed(self.status):
                self.error = self._get_error_message()
                if on_error := self.events.get("onError"):
                    on_error({"message": self.error})
            else:
                if on_finish := self.events.get("onFinish"):
                    on_finish(self.return_value)

            self.is_polling = False

        except Exception as e:
            self.is_polling = False
            raise e

    def _is_done(self, status: Optional[ExecutionStatus] = None) -> bool:
        return status not in [ExecutionStatus.CREATED, ExecutionStatus.RUNNING]

    def _is_failed(self, status: Optional[ExecutionStatus] = None) -> bool:
        return status in [
            ExecutionStatus.ERROR,
            ExecutionStatus.KILLED,
            ExecutionStatus.REJECTED,
        ]

    def _get_polling_interval(self) -> float:
        if self.poll_attempts < 4:
            return 0.25
        elif self.poll_attempts < 12:
            return 0.5
        return 1.0

    def _log_already_processed(self, log: Log) -> bool:
        return any(
            l.timestamp == log.timestamp and l.message == log.message for l in self.logs
        )

    def _get_error_message(self) -> str:
        return next(
            (e.explanation for e in (self.timeline or []) if e.status == self.status),
            next(
                (log.message for log in reversed(self.logs) if log.level == "ERROR"),
                None,
            ),
        )

    def kill(self) -> None:
        try:
            self.yepcode_api.kill_execution(self.id)
        except Exception as error:
            if getattr(error, "status", None) == 404:
                raise ValueError(f"Execution not found for id: {self.id}")
            raise error

    def rerun(self) -> "Execution":
        try:
            execution_id = self.yepcode_api.rerun_execution(self.id)
            return Execution(
                yepcode_api=self.yepcode_api,
                execution_id=execution_id,
                events=self.events,
            )
        except Exception as error:
            if getattr(error, "status", None) == 404:
                raise ValueError(f"Execution not found for id: {self.id}")
            raise error
