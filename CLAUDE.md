# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_language_detector.py

# Run a single test function
poetry run pytest tests/test_yepcode_run.py::test_run_python_code

# Run with coverage
poetry run pytest --cov=yepcode_run

# Build the package
poetry build
```

Tests require a `YEPCODE_API_TOKEN` environment variable. Set it in `.env` or export it before running tests. Most tests are integration tests that hit the live YepCode cloud API.

## Architecture

The SDK is a thin Python client for executing code in YepCode's serverless runtime.

**Layers:**

1. **Public API** — `YepCodeRun`, `YepCodeEnv`, `YepCodeStorage` (in `yepcode_run/`)
2. **Execution engine** — `yepcode_run/run/execution.py` handles polling loop, status transitions (`CREATED → RUNNING → FINISHED/ERROR`), and event callbacks (`onLog`, `onFinish`, `onError`)
3. **API Manager** — `yepcode_run/api/api_manager.py` singleton keyed by config hash; merges env vars + constructor params
4. **HTTP client** — `yepcode_run/api/yepcode_api.py` handles auth (API token or JWT with auto-refresh), all REST calls

**Key design decisions:**
- `YepCodeRun` hashes submitted code (SHA256) to reuse existing cloud processes rather than creating new ones each run
- `YepCodeApiManager` uses a singleton per config hash, so multiple `YepCodeRun` instances with the same credentials share one API client
- Language detection (`yepcode_run/utils/language_detector.py`) uses a score-based heuristic on stripped code (comments removed) when `language` is not specified

**Config priority:** constructor params > environment variables > `.env` file. Key env vars: `YEPCODE_API_TOKEN`, `YEPCODE_API_HOST` (defaults to `https://cloud.yepcode.io`), `YEPCODE_TIMEOUT` (ms, default 60000).

## OpenAPI spec

The live spec is always available at `https://cloud.yepcode.io/api/rest/public/api-docs`. Fetch it with WebFetch to audit which endpoints are missing from `yepcode_run/api/yepcode_api.py` before adding new ones. New endpoints are deployed to that URL before this SDK is updated.
