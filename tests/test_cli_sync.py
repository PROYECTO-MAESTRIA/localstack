"""
Tests del comando `shadowstack sync`: validan el pull completo, la exclusión
de recursos que van a cambiar (según --plan), y que --full la ignora.
Se mockean read_lambda_functions/write_lambda_function: no requieren AWS
real ni LocalStack.
"""
from __future__ import annotations

import json

from typer.testing import CliRunner

from shadowstack.cli import app
from shadowstack.sync.aws_reader import LambdaFunctionState

runner = CliRunner()


def _state(name: str) -> LambdaFunctionState:
    return LambdaFunctionState(
        function_name=name,
        runtime="python3.12",
        handler="handler.lambda_handler",
        memory_size=128,
        timeout=10,
        role_arn="arn:aws:iam::000000000000:role/irrelevant",
        code_zip=b"zip",
    )


def _write_plan(tmp_path, function_name: str) -> str:
    plan = {
        "resource_changes": [
            {
                "address": f"aws_lambda_function.{function_name}",
                "type": "aws_lambda_function",
                "name": function_name,
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {
                    "actions": ["update"],
                    "before": {"function_name": function_name, "memory_size": 128},
                    "after": {"function_name": function_name, "memory_size": 512},
                },
            }
        ]
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return str(plan_path)


def test_sync_sin_plan_sincroniza_todo(monkeypatch):
    written = []
    monkeypatch.setattr("shadowstack.cli.read_lambda_functions", lambda: [_state("a"), _state("b")])
    monkeypatch.setattr(
        "shadowstack.cli.write_lambda_function", lambda state: written.append(state.function_name)
    )

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0
    assert written == ["a", "b"]


def test_sync_con_plan_excluye_recurso_que_va_a_cambiar(monkeypatch, tmp_path):
    written = []
    monkeypatch.setattr("shadowstack.cli.read_lambda_functions", lambda: [_state("a"), _state("b")])
    monkeypatch.setattr(
        "shadowstack.cli.write_lambda_function", lambda state: written.append(state.function_name)
    )
    plan_path = _write_plan(tmp_path, "a")

    result = runner.invoke(app, ["sync", "--plan", plan_path])

    assert result.exit_code == 0
    assert written == ["b"]
    assert "excluida" in result.stdout


def test_sync_con_plan_y_full_ignora_exclusion(monkeypatch, tmp_path):
    written = []
    monkeypatch.setattr("shadowstack.cli.read_lambda_functions", lambda: [_state("a"), _state("b")])
    monkeypatch.setattr(
        "shadowstack.cli.write_lambda_function", lambda state: written.append(state.function_name)
    )
    plan_path = _write_plan(tmp_path, "a")

    result = runner.invoke(app, ["sync", "--plan", plan_path, "--full"])

    assert result.exit_code == 0
    assert written == ["a", "b"]
