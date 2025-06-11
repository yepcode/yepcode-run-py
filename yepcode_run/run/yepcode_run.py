import hashlib
from typing import Optional, Dict, Any

from ..api.api_manager import YepCodeApiManager
from ..api.yepcode_api import YepCodeApi, YepCodeApiError
from ..api.types import YepCodeApiConfig
from ..utils.language_detector import LanguageDetector
from .execution import Execution


class YepCodeRun:
    def __init__(self, config: Optional[YepCodeApiConfig] = None):
        """Initialize YepCodeRun with optional configuration."""
        self.yepcode_api = YepCodeApiManager.get_instance(config)
        self.PROCESS_NAME_PREFIX = "yepcode-run-"

    def get_client_id(self) -> str:
        return self._yepcode_api.get_client_id()

    def get_team_id(self) -> str:
        return self._yepcode_api.get_team_id()

    def _get_process_slug(self, hash_value: str) -> str:
        """Generate a process slug from a hash value."""
        return f"{self.PROCESS_NAME_PREFIX}{hash_value}"

    def create_process(
        self, code: str, language: str, manifest: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new process or return existing one."""
        if not language or not code:
            raise ValueError("language and code are required")

        process_slug = self._get_process_slug(hashlib.sha256(code.encode()).hexdigest())

        try:
            existing_process = self.yepcode_api.get_process(process_slug)
            if existing_process:
                return existing_process["id"]
        except YepCodeApiError as error:
            if error.status != 404:
                raise error

        process = self.yepcode_api.create_process(
            {
                "name": process_slug,
                "script": {
                    "programmingLanguage": language.upper(),
                    "sourceCode": code,
                },
                "tags": ["yc-run"],
                **(
                    {"manifest": manifest}
                    if manifest
                    else {
                        "settings": {
                            "dependencies": {
                                "scopedToProcess": True,
                                "autoDetect": True,
                            }
                        }
                    }
                ),
            }
        )
        return process["id"]

    def run(self, code: str, options: Dict[str, Any] = None) -> Execution:
        """Run code with specified options."""
        if options is None:
            options = {}

        language = options.get("language", LanguageDetector.detect_language(code))
        remove_on_done = options.get("removeOnDone", False)
        manifest = options.get("manifest")
        parameters = options.get("parameters", {})

        process_id = self.create_process(
            code=code, language=language, manifest=manifest
        )

        execution_response = self.yepcode_api.execute_process_async(
            process_id, parameters, options
        )

        if remove_on_done:
            original_on_finish = options.get("onFinish", lambda x: None)
            original_on_error = options.get("onError", lambda x: None)

            def wrapped_on_finish(return_value):
                self.yepcode_api.delete_process(process_id)
                original_on_finish(return_value)

            def wrapped_on_error(error):
                self.yepcode_api.delete_process(process_id)
                original_on_error(error)

            options["onFinish"] = wrapped_on_finish
            options["onError"] = wrapped_on_error

        execution = Execution(
            yepcode_api=self.yepcode_api,
            execution_id=execution_response["executionId"],
            events={
                "onLog": options.get("onLog", lambda x: None),
                "onFinish": options.get("onFinish", lambda x: None),
                "onError": options.get("onError", lambda x: None),
            },
        )
        return execution

    def get_execution(self, execution_id: str) -> Execution:
        """Get an existing execution by ID."""
        if not execution_id:
            raise ValueError("executionId is required")

        execution = Execution(yepcode_api=self.yepcode_api, execution_id=execution_id)
        return execution
