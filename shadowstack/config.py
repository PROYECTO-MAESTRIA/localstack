"""
Configuración central de ShadowStack: clientes boto3 para LocalStack (el gemelo)
y para AWS real (usado por el Sync Engine para leer el estado a replicar).
"""
from __future__ import annotations

import os
from functools import lru_cache

import boto3
from botocore.client import BaseClient
from dotenv import load_dotenv

load_dotenv()

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
LOCALSTACK_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")

# Servicios en scope del prototipo (sección 4.1 del documento de contexto)
LOCALSTACK_SERVICES = ["lambda", "apigateway", "dynamodb", "cloudwatch", "logs"]


def _localstack_session() -> boto3.Session:
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=LOCALSTACK_REGION,
    )


@lru_cache(maxsize=None)
def localstack_client(service_name: str) -> BaseClient:
    """
    Cliente boto3 apuntando al gemelo digital (LocalStack).
    Cacheado por servicio para no recrear conexiones innecesariamente.
    """
    if service_name not in LOCALSTACK_SERVICES:
        raise ValueError(
            f"Servicio '{service_name}' fuera del alcance del prototipo. "
            f"Servicios soportados: {LOCALSTACK_SERVICES}"
        )
    return _localstack_session().client(service_name, endpoint_url=LOCALSTACK_ENDPOINT)


@lru_cache(maxsize=None)
def real_aws_client(service_name: str) -> BaseClient:
    """
    Cliente boto3 apuntando a AWS real, usado por el Sync Engine (aws_reader.py)
    para leer el estado que será replicado en el gemelo.
    """
    session = boto3.Session(
        profile_name=os.getenv("AWS_REAL_PROFILE") or None,
        region_name=os.getenv("AWS_REAL_REGION"),
    )
    return session.client(service_name)
