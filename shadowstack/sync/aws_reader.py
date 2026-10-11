"""
AWS Reader: lee el estado actual de los recursos reales de AWS (en los
servicios en scope del prototipo) para que el Sync Engine los replique
en el gemelo digital (LocalStack).
"""
from __future__ import annotations

import requests
from pydantic import BaseModel

from shadowstack.config import real_aws_client


class LambdaFunctionState(BaseModel):
    function_name: str
    runtime: str
    handler: str
    memory_size: int
    timeout: int
    role_arn: str
    code_zip: bytes


def _download_code(location: str) -> bytes:
    """Descarga el paquete de despliegue (.zip) desde la URL firmada que devuelve AWS."""
    response = requests.get(location, timeout=30)
    response.raise_for_status()
    return response.content


def read_lambda_functions() -> list[LambdaFunctionState]:
    """Lee todas las funciones Lambda desplegadas en AWS real, incluyendo su código."""
    client = real_aws_client("lambda")
    states = []
    paginator = client.get_paginator("list_functions")
    for page in paginator.paginate():
        for fn in page["Functions"]:
            detail = client.get_function(FunctionName=fn["FunctionName"])
            code_zip = _download_code(detail["Code"]["Location"])
            states.append(
                LambdaFunctionState(
                    function_name=fn["FunctionName"],
                    runtime=fn["Runtime"],
                    handler=fn["Handler"],
                    memory_size=fn["MemorySize"],
                    timeout=fn["Timeout"],
                    role_arn=fn["Role"],
                    code_zip=code_zip,
                )
            )
    return states
