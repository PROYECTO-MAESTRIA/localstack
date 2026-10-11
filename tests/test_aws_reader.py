"""
Tests de AWS Reader: usan moto para simular AWS real, sin necesitar
credenciales ni conexión de red reales.
"""
from __future__ import annotations

import io
import zipfile

import boto3
import pytest
from moto import mock_aws

from shadowstack.config import real_aws_client
from shadowstack.sync.aws_reader import read_lambda_functions


def _zip_bytes(code: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("handler.py", code)
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _real_aws_client_aislado(monkeypatch):
    # Evita que el profile real del desarrollador (AWS_REAL_PROFILE en su .env)
    # interfiera con moto, y evita reusar clientes cacheados entre tests.
    monkeypatch.delenv("AWS_REAL_PROFILE", raising=False)
    real_aws_client.cache_clear()
    yield
    real_aws_client.cache_clear()


@mock_aws
def test_read_lambda_functions_lee_config_y_codigo(monkeypatch):
    # moto no sirve el .zip real detrás de la URL de Code.Location (siempre
    # devuelve 404), así que aislamos esa descarga puntual y probamos la
    # parte que sí simula de verdad: la lectura de configuración.
    monkeypatch.setattr(
        "shadowstack.sync.aws_reader._download_code", lambda location: b"contenido-zip-simulado"
    )

    iam = boto3.client("iam", region_name="us-east-2")
    role_arn = iam.create_role(
        RoleName="test-role",
        AssumeRolePolicyDocument="{}",
    )["Role"]["Arn"]

    lam = boto3.client("lambda", region_name="us-east-2")
    lam.create_function(
        FunctionName="shadowstack-caso01-memoria",
        Runtime="python3.12",
        Role=role_arn,
        Handler="handler.lambda_handler",
        Code={"ZipFile": _zip_bytes("def lambda_handler(e, c): return {}")},
        MemorySize=128,
        Timeout=10,
    )

    functions = read_lambda_functions()

    assert len(functions) == 1
    f = functions[0]
    assert f.function_name == "shadowstack-caso01-memoria"
    assert f.runtime == "python3.12"
    assert f.handler == "handler.lambda_handler"
    assert f.memory_size == 128
    assert f.timeout == 10
    assert f.role_arn == role_arn
    assert f.code_zip == b"contenido-zip-simulado"


@mock_aws
def test_read_lambda_functions_sin_funciones_devuelve_lista_vacia():
    assert read_lambda_functions() == []
