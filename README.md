# YepCode Run

A powerful serverless runtime and SDK for executing code in secure sandboxes, with a complete platform for building, managing, and monitoring your script executions.

Built on top of [YepCode Cloud](https://yepcode.io/), the enterprise platform that enables seamless script execution for AI agents, data processing, API integrations, and automation workflows.

## Try it Now!

Ready to see it in action? Visit our 🎮 [interactive playground](https://yepcode.io/run) (no registration required) where you can:

- Test code execution in real-time
- Experiment with different languages and packages
- Learn through hands-on examples

## Why YepCode Run?

Running arbitrary code in production environments presents significant challenges around security, scalability, and infrastructure management. This is especially critical when dealing with **AI-generated code** from LLMs, where code execution needs to be both secure and reliable at scale and may also need to install external dependencies.

YepCode Run eliminates these complexities by providing enterprise-grade sandboxing, automatic scaling, and comprehensive security measures out of the box - allowing you to focus on your code instead of infrastructure concerns.

## 🚀 Features

- 🚀 **Instant Code Execution** - Run JavaScript and Python code in secure sandboxes without any setup
- 🔒 **Enterprise-Ready Platform** - Full suite of tools for building, deploying and monitoring processes
- 🔄 **Built for Integration** - Perfect for AI agents, data processing, API integrations and automation workflows
- 📊 **Complete Observability** - Monitor executions, manage credentials, and audit changes in one place
- 🛠️ **Developer Experience** - Write code in our web IDE or use our API/SDK to integrate with your apps
- 📦 **Package Freedom** - Use any external dependency with automatic package detection or specify exact versions using `@add-package` annotations

## 🔧 Installation

```bash
pip install yepcode_run
```

## 🔑 Get your YepCode API token

You can get your YepCode API token from the [YepCode Cloud](https://cloud.yepcode.io) platform under `Settings` > `API credentials`.

This token may be provided to the `YepCodeRun`, `YepCodeEnv` or `YepCodeApi` constructor, or set in the `YEPCODE_API_TOKEN` environment variable.

```env
YEPCODE_API_TOKEN=your-api-token
```

## 💻 Usage

### ⚡ Code Execution

The `YepCodeRun` class provides flexible code execution capabilities:

```python
from yepcode_run import YepCodeRun

runner = YepCodeRun(
    api_token='your-api-token'  # We'll try to read it from the YEPCODE_API_TOKEN environment variable
)

# Execute code with full options
execution = runner.run(
    """def main():
    message = "Hello, YepCode!"
    print(message)
    return {"message": message}""",
    {
        "language": "python",  # Optional - auto-detected if not specified
        "onLog": lambda log: print(f"{log.timestamp} {log.level}: {log.message}"),
        "onFinish": lambda return_value: print("Finished:", return_value),
        "onError": lambda error: print("Error:", error)
    }
)

# Wait for execution to complete
execution.wait_for_done()

# Retrieve an existing execution
existing_execution = runner.get_execution('execution-id')
```

### 🔐 Environment Variables

You may use environment variables in your code with `process.env` (JavaScript) or `os.getenv` (Python), and you may manage this environment variables in the YepCode platform ([docs here](https://yepcode.io/docs/processes/team-variables)), or using this `YepCodeEnv` class:

```python
from yepcode_run import YepCodeEnv

env = YepCodeEnv(
    api_token='your-api-token'
)

# Set environment variables
env.set_env_var('API_KEY', 'secret-value')           # Sensitive by default
env.set_env_var('DEBUG', 'true', False)             # Non-sensitive variable

# Get all environment variables
variables = env.get_env_vars()
# Returns: [TeamVariable(key='API_KEY', value='secret-value'), TeamVariable(key='DEBUG', value='true')]

# Delete an environment variable
env.del_env_var('API_KEY')
```

### 🌐 Direct API access

You can also directly access the full [YepCode API](https://yepcode.io/docs/api) using the `YepCodeApi` class:

```python
from yepcode_run import YepCodeApi

api = YepCodeApi(
  api_token='your-api-token'
)

# Get all processes
processes = await api.get_processes()
```


## 📚 SDK API Reference

### ⚡ YepCodeRun

#### Methods

- `run(code: str, options: Optional[Dict[str, Any]] = None) -> Execution`
  - `code`: Source code to execute
  - `options`:
    - `language`: Programming language ('javascript' or 'python')
    - `onLog`: Log event handler
    - `onFinish`: Success completion handler
    - `onError`: Error handler
    - `removeOnDone`: Auto-cleanup after execution. If you don't clean up, executions will be available in YepCode Cloud.
    - `parameters`: Execution parameters (see [docs](https://yepcode.io/docs/processes/input-params) for more information)
    - `manifest`: Custom process manifest (see [docs](https://yepcode.io/docs/dependencies) for more information)

- `get_execution(execution_id: str) -> Execution`
  - Retrieves an existing execution by ID

#### `Execution` class properties

- `execution_id: str` - Unique identifier for the execution
- `logs: List[Log]` - Array of execution logs with timestamps, log levels, and messages
- `process_id: Optional[str]` - ID of the associated process
- `status: Optional[ExecutionStatus]` - Current execution status
- `return_value: Any` - Execution result (if completed successfully)
- `error: Optional[str]` - Error message (if execution failed)
- `timeline: Optional[List[TimelineEvent]]` - Execution timeline events
- `parameters: Any` - Execution input parameters
- `comment: Optional[str]` - Execution comment

#### `Execution` class methods

- `is_done() -> bool`
  - Returns whether the execution has completed (successfully or with error)

- `wait_for_done() -> None`
  - Waits for the execution to complete

- `kill() -> None`
  - Terminates the execution

- `rerun() -> Execution`
  - Creates a new execution with the same configuration

### 🔐 YepCodeEnv

#### Methods

- `get_env_vars() -> List[TeamVariable]`
  - Returns all environment variables

- `set_env_var(key: str, value: str, is_sensitive: Optional[bool] = True) -> None`
  - Sets an environment variable
  - `is_sensitive`: Marks variable as sensitive (defaults to True)

- `del_env_var(key: str) -> None`
  - Deletes an environment variable

## 📄 License

All rights reserved by YepCode. This package is part of the YepCode Platform and is subject to the [YepCode Terms of Service](https://yepcode.io/terms-of-use).