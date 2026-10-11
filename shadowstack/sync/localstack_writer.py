"""
LocalStack Writer: crea o actualiza en el gemelo digital (LocalStack) los
recursos leídos de AWS real por aws_reader.py.
"""
from __future__ import annotations

from botocore.exceptions import ClientError

from shadowstack.config import localstack_client
from shadowstack.sync.aws_reader import LambdaFunctionState


def _function_exists(client, function_name: str) -> bool:
    try:
        client.get_function(FunctionName=function_name)
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise


def _wait_until_stable(client, function_name: str) -> None:
    """
    Lambda deja la función en estado 'Pending'/'InProgress' un instante
    después de crearla o actualizarla; cualquier otra operación mientras
    tanto falla con ResourceConflictException (pasa igual en AWS real).
    """
    client.get_waiter("function_active_v2").wait(FunctionName=function_name)
    client.get_waiter("function_updated_v2").wait(FunctionName=function_name)


def write_lambda_function(state: LambdaFunctionState) -> None:
    """
    Crea la función Lambda en LocalStack si no existe, o actualiza su código
    y configuración si ya existe. El `role_arn` se copia tal cual desde AWS
    real: LocalStack no valida que el rol IAM exista de verdad.
    """
    client = localstack_client("lambda")

    if not _function_exists(client, state.function_name):
        client.create_function(
            FunctionName=state.function_name,
            Runtime=state.runtime,
            Role=state.role_arn,
            Handler=state.handler,
            Code={"ZipFile": state.code_zip},
            MemorySize=state.memory_size,
            Timeout=state.timeout,
        )
        _wait_until_stable(client, state.function_name)
        return

    _wait_until_stable(client, state.function_name)
    client.update_function_code(FunctionName=state.function_name, ZipFile=state.code_zip)
    _wait_until_stable(client, state.function_name)
    client.update_function_configuration(
        FunctionName=state.function_name,
        Runtime=state.runtime,
        Role=state.role_arn,
        Handler=state.handler,
        MemorySize=state.memory_size,
        Timeout=state.timeout,
    )
