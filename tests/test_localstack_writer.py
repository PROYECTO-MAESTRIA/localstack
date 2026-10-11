"""
Tests de LocalStack Writer: crean/actualizan Lambdas de verdad en LocalStack.

Requiere LocalStack activo. Se puede saltar en CI sin Docker con:
    pytest -m "not requires_localstack"
"""
from __future__ import annotations

import io
import zipfile

import pytest

from shadowstack.config import localstack_client
from shadowstack.sync.aws_reader import LambdaFunctionState
from shadowstack.sync.localstack_writer import write_lambda_function

pytestmark = pytest.mark.requires_localstack

_FUNCTION_NAME = "shadowstack-test-writer"


def _zip_bytes(code: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("handler.py", code)
    return buf.getvalue()


def _sample_state(**overrides) -> LambdaFunctionState:
    defaults = dict(
        function_name=_FUNCTION_NAME,
        runtime="python3.12",
        handler="handler.lambda_handler",
        memory_size=128,
        timeout=10,
        role_arn="arn:aws:iam::000000000000:role/irrelevant-role",
        code_zip=_zip_bytes("def lambda_handler(e, c): return {}"),
    )
    defaults.update(overrides)
    return LambdaFunctionState(**defaults)


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    client = localstack_client("lambda")
    try:
        client.delete_function(FunctionName=_FUNCTION_NAME)
    except client.exceptions.ResourceNotFoundException:
        pass


def test_write_lambda_function_crea_si_no_existe():
    write_lambda_function(_sample_state())

    client = localstack_client("lambda")
    created = client.get_function(FunctionName=_FUNCTION_NAME)["Configuration"]
    assert created["MemorySize"] == 128
    assert created["Runtime"] == "python3.12"


def test_write_lambda_function_actualiza_si_ya_existe():
    write_lambda_function(_sample_state())
    write_lambda_function(_sample_state(memory_size=512))

    client = localstack_client("lambda")
    updated = client.get_function(FunctionName=_FUNCTION_NAME)["Configuration"]
    assert updated["MemorySize"] == 512
