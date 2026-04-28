import time
from datetime import datetime, timezone

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
