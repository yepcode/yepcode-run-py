import os
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
import requests

from yepcode_run import YepCodeStorage
from yepcode_run.api.yepcode_api import YepCodeApiError


TEST_NAME = "test-run-sdk.txt"
TEST_CONTENT = b"hello signed url"


@pytest.fixture
def storage():
    return YepCodeStorage()


@pytest.fixture
def uploaded_file(storage):
    storage.upload(TEST_NAME, TEST_CONTENT)
    yield TEST_NAME
    try:
        storage.delete(TEST_NAME)
    except Exception:
        pass


def _parse_iso(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


@pytest.mark.skipif(
    os.getenv("RUN_SIGNED_URL_TESTS", "false").lower() != "true",
    reason="Set RUN_SIGNED_URL_TESTS=true to run signed URL end-to-end tests.",
)
def test_create_signed_url_e2e_matches_js_flow(storage):
    file_name = f"sdk-signed-url-test-{uuid.uuid4().hex}.txt"
    original_content = f"signed-url-test-content-{int(time.time() * 1000)}"

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as temp_file:
        temp_file.write(original_content)
        local_file_path = Path(temp_file.name)

    try:
        storage.upload(file_name, local_file_path.read_bytes())
        signed_url = storage.create_signed_url(file_name, expires_in_seconds=120)

        assert isinstance(signed_url.url, str)
        assert len(signed_url.url) > 0
        assert signed_url.path == file_name
        assert _parse_iso(signed_url.expires_at) > time.time()

        print(signed_url.url)

        response = requests.get(signed_url.url, timeout=30)
        assert response.ok
        assert response.text == original_content
    finally:
        try:
            storage.delete(file_name)
            pass
        except Exception:
            pass

        if local_file_path.exists():
            local_file_path.unlink()


@pytest.mark.skip(reason="Requires the signed-urls endpoint deployed in the target environment")
def test_create_signed_url_default_expiry(storage, uploaded_file):
    result = storage.create_signed_url(uploaded_file)

    assert isinstance(result.url, str) and len(result.url) > 0
    assert result.path == uploaded_file

    expires_at = _parse_iso(result.expires_at)
    expected_expiry = time.time() + 3600
    assert abs(expires_at - expected_expiry) < 60


@pytest.mark.skip(reason="Requires the signed-urls endpoint deployed in the target environment")
def test_create_signed_url_custom_expiry(storage, uploaded_file):
    result = storage.create_signed_url(uploaded_file, expires_in_seconds=60)

    expires_at = _parse_iso(result.expires_at)
    expected_expiry = time.time() + 60
    assert abs(expires_at - expected_expiry) < 30


@pytest.mark.skip(reason="Requires the signed-urls endpoint deployed in the target environment")
def test_create_signed_url_returns_fetchable_url(storage, uploaded_file):
    result = storage.create_signed_url(uploaded_file)

    response = requests.get(result.url, timeout=30)
    assert response.ok
    assert response.content == TEST_CONTENT


@pytest.mark.skip(reason="Requires the signed-urls endpoint deployed in the target environment")
def test_create_signed_url_missing_file_raises_404(storage):
    with pytest.raises(YepCodeApiError) as exc_info:
        storage.create_signed_url("does-not-exist.txt")
    assert exc_info.value.status == 404


@pytest.mark.skip(reason="Requires the signed-urls endpoint deployed in the target environment")
def test_create_signed_url_out_of_range_expiry_raises_400(storage, uploaded_file):
    with pytest.raises(YepCodeApiError) as exc_info:
        storage.create_signed_url(uploaded_file, expires_in_seconds=999999)
    assert exc_info.value.status == 400
