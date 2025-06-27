![YepCode Run SDK Preview](/readme-assets/cover.png)

<div align="center">

[![PyPI Version](https://img.shields.io/pypi/v/yepcode-run)](https://pypi.org/project/yepcode-run/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/yepcode-run)](https://pypi.org/project/yepcode-run/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/yepcode/yepcode-run-py/ci.yml)](https://github.com/yepcode/yepcode-run-py/actions)

</div>

## What is YepCode Run?

[YepCode Run](https://yepcode.io/run) is a powerful serverless runtime that enables secure code execution in isolated sandboxes. With our comprehensive SDK and platform, you can effortlessly build, manage, and monitor your script executions. Get started quickly using our [JavaScript SDK](https://www.npmjs.com/package/@yepcode/run) or [Python SDK](https://pypi.org/project/yepcode-run).

Powered by [YepCode Cloud](https://yepcode.io/), our enterprise-grade platform delivers seamless script execution capabilities for AI agents, data processing pipelines, API integrations, and automation workflows. Focus on your code while we handle the infrastructure.

## Quick start

### 1. Installation

```bash
pip install yepcode-run
```

### 2. Get your YepCode API token

1. Sign up to [YepCode Cloud](https://cloud.yepcode.io)
2. Get your API token from your workspace under: `Settings` > `API credentials`
3. Use your API token securely in one of these ways:

   ```python
   # Option 1: Set as environment variable (Recommended)
   # .env file
   YEPCODE_API_TOKEN=your_token_here

   # Option 2: Provide directly to the constructor (Not recommended for production)
   runner = YepCodeRun(YepCodeApiConfig(api_token='your_token_here'))
   ```

### 3. Execute your code

```python
from yepcode_run import YepCodeRun, YepCodeApiConfig

runner = YepCodeRun(
    YepCodeApiConfig(api_token='your-api-token')
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

### 4. Manage Environment Variables

You may use environment variables in your code with `process.env` (JavaScript) or `os.getenv` (Python), and you may manage this environment variables in the YepCode platform ([docs here](https://yepcode.io/docs/processes/team-variables)), or using this `YepCodeEnv` class:

```python
from yepcode_run import YepCodeEnv, YepCodeApiConfig

env = YepCodeEnv(
    YepCodeApiConfig(api_token='your-api-token')
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

### 5. Direct API access

You can also directly access the full [YepCode API](https://yepcode.io/docs/api) using the `YepCodeApi` class:

```python
from yepcode_run import YepCodeApi, YepCodeApiConfig

api = YepCodeApi(
  YepCodeApiConfig(api_token='your-api-token')
)

# Get all processes
processes = api.get_processes()
```

### 6. YepCode Storage

You can manage files in your YepCode workspace using the `YepCodeStorage` class. This allows you to upload, list, download, and delete files easily.

```python
from yepcode_run import YepCodeStorage, YepCodeApiConfig

storage = YepCodeStorage(
    YepCodeApiConfig(api_token='your-api-token')
)

# Upload a file
with open('myfile.txt', 'rb') as f:
    obj = storage.upload('myfile.txt', f)
    print('Uploaded:', obj.name, obj.size, obj.link)

# List all storage objects
objects = storage.list()
for obj in objects:
    print(obj.name, obj.size, obj.link)

# Download a file
content = storage.download('myfile.txt')
with open('downloaded.txt', 'wb') as f:
    f.write(content)

# Delete a file
storage.delete('myfile.txt')
```

## SDK API Reference

### YepCodeRun

The main class for executing code in YepCode's runtime environment.

#### Methods

##### `run(code: str, options: Optional[Dict[str, Any]] = None) -> Execution`

Executes code in YepCode's runtime environment.

**Parameters:**
- `code`: Source code to execute (string)
- `options`: Execution options (optional)
  ```python
  {
      "language": Optional[str],        # 'javascript' or 'python'
      "onLog": Optional[Callable],      # Log event handler
      "onFinish": Optional[Callable],   # Success completion handler
      "onError": Optional[Callable],    # Error handler
      "removeOnDone": Optional[bool],   # Auto-cleanup after execution
      "parameters": Optional[Any],      # Execution parameters
      "manifest": Optional[Dict],       # Custom process manifest
      "timeout": Optional[int]          # Execution timeout in ms
  }
  ```

**Returns:** Execution

##### `get_execution(execution_id: str) -> Execution`

Retrieves an existing execution by ID.

**Parameters:**
- `execution_id`: Unique identifier for the execution

**Returns:** Execution

#### `Execution` class

Represents a code execution instance.

**Properties:**
```python
class Execution:
    id: str                    # Unique identifier
    logs: List[Log]                      # Array of execution logs
    process_id: Optional[str]            # ID of the associated process
    status: Optional[ExecutionStatus]    # Current execution status
    return_value: Any                    # Execution result
    error: Optional[str]                 # Error message
    timeline: Optional[List[TimelineEvent]]  # Execution timeline events
    parameters: Any                      # Execution input parameters
    comment: Optional[str]               # Execution comment
```

**Methods:**

###### `is_done() -> bool`
Returns whether the execution has completed.

**Returns:** bool

###### `wait_for_done() -> None`
Waits for the execution to complete.

**Returns:** None

###### `kill() -> None`
Terminates the execution.

**Returns:** None

###### `rerun() -> Execution`
Creates a new execution with the same configuration.

**Returns:** Execution

### YepCodeEnv

Manages environment variables for your YepCode workspace.

#### Methods

##### `get_env_vars() -> List[TeamVariable]`
Returns all environment variables.

**Returns:** List[TeamVariable]
```python
class TeamVariable:
    key: str
    value: str
    is_sensitive: bool
```

##### `set_env_var(key: str, value: str, is_sensitive: bool = True) -> None`
Sets an environment variable.

**Parameters:**
- `key`: Variable name
- `value`: Variable value
- `is_sensitive`: Whether the variable contains sensitive data (defaults to true)

**Returns:** None

##### `del_env_var(key: str) -> None`
Deletes an environment variable.

**Parameters:**
- `key`: Variable name to delete

**Returns:** None

### YepCodeApi

Provides direct access to the YepCode API.

#### Methods

##### `get_processes() -> List[Process]`
Returns all available processes.

**Returns:** List[Process]
```python
class Process:
    id: str
    name: str
    description: Optional[str]
    created_at: str
```

### YepCodeStorage

The main class for managing files in YepCode's cloud storage.

#### Methods

##### `upload(name: str, file: bytes) -> StorageObject`
Uploads a file to YepCode storage.

**Parameters:**
- `name`: Name of the file in storage
- `file`: File content as bytes or a file-like object

**Returns:** StorageObject

##### `download(name: str) -> bytes`
Downloads a file from YepCode storage.

**Parameters:**
- `name`: Name of the file to download

**Returns:** File content as bytes

##### `delete(name: str) -> None`
Deletes a file from YepCode storage.

**Parameters:**
- `name`: Name of the file to delete

**Returns:** None

##### `list() -> List[StorageObject]`
Lists all files in YepCode storage.

**Returns:** List of StorageObject

#### Types

```python
class StorageObject:
    name: str           # File name
    size: int           # File size in bytes
    md5_hash: str       # MD5 hash of the file
    content_type: str   # MIME type
    created_at: str     # Creation timestamp (ISO8601)
    updated_at: str     # Last update timestamp (ISO8601)
    link: str           # Download link

class CreateStorageObjectInput:
    name: str           # File name
    file: Any           # File content (bytes or file-like)
```

## License

All rights reserved by YepCode. This package is part of the YepCode Platform and is subject to the [YepCode Terms of Service](https://yepcode.io/terms-of-use).