"""
Tests del Diff Parser: validan que un plan.json de Terraform (formato de
`terraform show -json`) se normaliza correctamente a PlanDiff/ResourceChange,
sin necesidad de LocalStack ni Terraform instalados.
"""
from __future__ import annotations

import json

import pytest

from shadowstack.sync.diff_parser import ChangeAction, parse_plan, parse_plan_dict

SAMPLE_PLAN = {
    "terraform_version": "1.7.0",
    "resource_changes": [
        {
            "address": "aws_lambda_function.facturacion",
            "type": "aws_lambda_function",
            "name": "facturacion",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {
                "actions": ["create"],
                "before": None,
                "after": {"memory_size": 128},
            },
        },
        {
            "address": "aws_dynamodb_table.facturas",
            "type": "aws_dynamodb_table",
            "name": "facturas",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {
                "actions": ["update"],
                "before": {"billing_mode": "PROVISIONED"},
                "after": {"billing_mode": "PAY_PER_REQUEST"},
            },
        },
        {
            "address": "aws_iam_role.legacy",
            "type": "aws_iam_role",
            "name": "legacy",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {
                "actions": ["delete"],
                "before": {"name": "legacy"},
                "after": None,
            },
        },
        {
            "address": "aws_lambda_function.memoria",
            "type": "aws_lambda_function",
            "name": "memoria",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {
                "actions": ["delete", "create"],
                "before": {"memory_size": 128},
                "after": {"memory_size": 512},
            },
        },
        {
            "address": "aws_apigatewayv2_api.publica",
            "type": "aws_apigatewayv2_api",
            "name": "publica",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {
                "actions": ["no-op"],
                "before": {"name": "publica"},
                "after": {"name": "publica"},
            },
        },
    ],
}


def test_parse_plan_dict_clasifica_cada_accion():
    diff = parse_plan_dict(SAMPLE_PLAN)

    assert [c.address for c in diff.to_create] == ["aws_lambda_function.facturacion"]
    assert [c.address for c in diff.to_update] == ["aws_dynamodb_table.facturas"]
    assert [c.address for c in diff.to_delete] == ["aws_iam_role.legacy"]
    assert [c.address for c in diff.to_replace] == ["aws_lambda_function.memoria"]


def test_parse_plan_dict_preserva_terraform_version():
    diff = parse_plan_dict(SAMPLE_PLAN)
    assert diff.terraform_version == "1.7.0"


def test_parse_plan_dict_preserva_before_after():
    diff = parse_plan_dict(SAMPLE_PLAN)
    tabla = diff.to_update[0]
    assert tabla.before == {"billing_mode": "PROVISIONED"}
    assert tabla.after == {"billing_mode": "PAY_PER_REQUEST"}


def test_changed_addresses_excluye_no_op():
    diff = parse_plan_dict(SAMPLE_PLAN)
    assert diff.changed_addresses == {
        "aws_lambda_function.facturacion",
        "aws_dynamodb_table.facturas",
        "aws_iam_role.legacy",
        "aws_lambda_function.memoria",
    }
    assert "aws_apigatewayv2_api.publica" not in diff.changed_addresses


def test_recurso_no_op_se_parsea_pero_no_se_clasifica():
    diff = parse_plan_dict(SAMPLE_PLAN)
    no_op = next(c for c in diff.resource_changes if c.address == "aws_apigatewayv2_api.publica")
    assert no_op.action == ChangeAction.NO_OP


def test_accion_no_reconocida_lanza_error():
    plan_invalido = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.x",
                "type": "aws_s3_bucket",
                "name": "x",
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {"actions": ["import"], "before": None, "after": None},
            }
        ]
    }
    with pytest.raises(ValueError):
        parse_plan_dict(plan_invalido)


def test_parse_plan_lee_desde_archivo(tmp_path):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(SAMPLE_PLAN), encoding="utf-8")

    diff = parse_plan(plan_path)

    assert len(diff.resource_changes) == 5
    assert len(diff.to_create) == 1
