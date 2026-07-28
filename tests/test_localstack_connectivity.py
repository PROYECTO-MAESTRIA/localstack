"""
Test de humo: valida que, con LocalStack corriendo (docker-compose up),
los clientes boto3 configurados en shadowstack.config responden en los
tres servicios en scope del prototipo.

Requiere LocalStack activo. Se puede saltar en CI sin Docker con:
    pytest -m "not requires_localstack"
"""
from __future__ import annotations

import pytest

from shadowstack.config import localstack_client

pytestmark = pytest.mark.requires_localstack


def test_lambda_list_functions_responde():
    client = localstack_client("lambda")
    response = client.list_functions()
    assert "Functions" in response


def test_apigateway_get_rest_apis_responde():
    client = localstack_client("apigateway")
    response = client.get_rest_apis()
    assert "items" in response


def test_dynamodb_list_tables_responde():
    client = localstack_client("dynamodb")
    response = client.list_tables()
    assert "TableNames" in response


def test_servicio_fuera_de_scope_lanza_error():
    with pytest.raises(ValueError):
        localstack_client("s3")
