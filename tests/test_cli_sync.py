"""
Tests del comando `shadowstack sync`: validan la regla de que omitir --plan
equivale a pedir un pull completo (--full), sin necesitar LocalStack ni un
plan.json real (el comando todavía no tiene lógica de sincronización).
"""
from __future__ import annotations

from typer.testing import CliRunner

from shadowstack.cli import app

runner = CliRunner()


def test_sync_sin_plan_activa_full():
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    assert "plan=None full=True" in result.stdout


def test_sync_con_plan_no_activa_full_por_defecto():
    result = runner.invoke(app, ["sync", "--plan", "plan.json"])
    assert result.exit_code == 0
    assert "plan=plan.json full=False" in result.stdout


def test_sync_con_plan_y_full_explicito():
    result = runner.invoke(app, ["sync", "--plan", "plan.json", "--full"])
    assert result.exit_code == 0
    assert "plan=plan.json full=True" in result.stdout
