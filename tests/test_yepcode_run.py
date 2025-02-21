import pytest
import secrets
from yepcode_run import YepCodeRun, YepCodeEnv, ExecutionStatus


def random_hex():
    return secrets.token_hex(2)


@pytest.fixture(scope="session")
def yep_code_env():
    env = YepCodeEnv()
    env.set_env_var("WORLD_ENV_VAR", "World", False)
    yield env
    env.del_env_var("WORLD_ENV_VAR")


@pytest.fixture
def yep_code_run():
    return YepCodeRun()


def test_manage_env_vars(yep_code_env):
    env_var_name = f"ENV_VAR_NAME_{random_hex()}"
    env_var_value = f"ENV_VAR_VALUE_{random_hex()}"
    env_var_value2 = f"ENV_VAR_VALUE_2_{random_hex()}"

    yep_code_env.set_env_var(env_var_name, env_var_value, False)
    env_vars = yep_code_env.get_env_vars()
    assert (
        next((var for var in env_vars if var.key == env_var_name), None).value
        == env_var_value
    )

    yep_code_env.set_env_var(env_var_name, env_var_value2, False)
    env_vars = yep_code_env.get_env_vars()
    assert (
        next((var for var in env_vars if var.key == env_var_name), None).value
        == env_var_value2
    )

    yep_code_env.del_env_var(env_var_name)
    env_vars = yep_code_env.get_env_vars()
    assert next((var for var in env_vars if var.key == env_var_name), None) is None


def test_run_javascript_code(yep_code_run):
    execution = yep_code_run.run(
        """async function main() {
    const message = `Hello, ${process.env.WORLD_ENV_VAR}!`
    console.log(message)
    return { message }
}

module.exports = {
    main,
};""",
        {"removeOnDone": True},
    )
    execution.wait_for_done()
    assert execution.status.value == "FINISHED"
    assert execution.return_value["message"] == "Hello, World!"


def test_run_python_code(yep_code_run):
    execution = yep_code_run.run(
        """import os

def main():
    message = f"Hello, {os.getenv('WORLD_ENV_VAR')}!"
    print(message)
    return {"message": message}""",
        {"removeOnDone": True},
    )
    execution.wait_for_done()
    assert execution.status == ExecutionStatus.FINISHED
    assert execution.return_value["message"] == "Hello, World!"


def test_trigger_on_log(yep_code_run):
    logs = []
    execution = yep_code_run.run(
        """async function main() {
    console.log("Log message 1")
    console.log("Log message 2")
    return { success: true }
}

module.exports = { main };""",
        {
            "removeOnDone": True,
            "onLog": lambda log_entry: logs.append(log_entry.message),
        },
    )

    execution.wait_for_done()
    assert "Log message 1" in logs
    assert "Log message 2" in logs


def test_trigger_on_finish(yep_code_run):
    finish_value = None

    def on_finish(return_value):
        nonlocal finish_value
        finish_value = return_value

    execution = yep_code_run.run(
        """async function main() {
    return { data: "test data" }
}

module.exports = { main };""",
        {"removeOnDone": True, "onFinish": on_finish},
    )

    execution.wait_for_done()
    assert finish_value == {"data": "test data"}


def test_trigger_on_error(yep_code_run):
    error_message = None

    def on_error(error):
        nonlocal error_message
        error_message = error["message"]

    execution = yep_code_run.run(
        """async function main() {
    throw new Error("Test error");
}

module.exports = { main };""",
        {"removeOnDone": True, "onError": on_error},
    )

    execution.wait_for_done()
    assert "Test error" in error_message


def test_handle_all_events_python(yep_code_run):
    logs = []
    finish_value = None

    def on_finish(return_value):
        nonlocal finish_value
        finish_value = return_value

    execution = yep_code_run.run(
        """def main():
    print("Log message 1")
    print("Log message 2")
    return {"data": "python test"}""",
        {
            "language": "python",
            "removeOnDone": True,
            "onLog": lambda log_entry: logs.append(log_entry.message),
            "onFinish": on_finish,
        },
    )

    execution.wait_for_done()
    assert "Log message 1" in logs
    assert "Log message 2" in logs
    assert finish_value == {"data": "python test"}
