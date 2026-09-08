"""
Diff Parser: interpreta el `plan.json` producido por Terraform
(`terraform show -json <plan> > plan.json`) y lo normaliza en un modelo
tipado que el resto del Sync Engine (aws_reader.py, localstack_writer.py)
y el comando `shadowstack sync` puedan consumir.
"""
from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ChangeAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"
    NO_OP = "no-op"


_ACTIONS_TO_CHANGE_ACTION: dict[frozenset[str], ChangeAction] = {
    frozenset({"create"}): ChangeAction.CREATE,
    frozenset({"update"}): ChangeAction.UPDATE,
    frozenset({"delete"}): ChangeAction.DELETE,
    frozenset({"create", "delete"}): ChangeAction.REPLACE,
    frozenset({"no-op"}): ChangeAction.NO_OP,
    frozenset(): ChangeAction.NO_OP,
}


def _action_from_raw(actions: list[str]) -> ChangeAction:
    key = frozenset(actions)
    try:
        return _ACTIONS_TO_CHANGE_ACTION[key]
    except KeyError:
        raise ValueError(f"Combinación de acciones de Terraform no reconocida: {actions}") from None


class ResourceChange(BaseModel):
    address: str
    resource_type: str
    name: str
    provider_name: str
    action: ChangeAction
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None


class PlanDiff(BaseModel):
    terraform_version: str | None = None
    resource_changes: list[ResourceChange] = Field(default_factory=list)

    @property
    def to_create(self) -> list[ResourceChange]:
        return [c for c in self.resource_changes if c.action == ChangeAction.CREATE]

    @property
    def to_update(self) -> list[ResourceChange]:
        return [c for c in self.resource_changes if c.action == ChangeAction.UPDATE]

    @property
    def to_delete(self) -> list[ResourceChange]:
        return [c for c in self.resource_changes if c.action == ChangeAction.DELETE]

    @property
    def to_replace(self) -> list[ResourceChange]:
        return [c for c in self.resource_changes if c.action == ChangeAction.REPLACE]

    @property
    def changed_addresses(self) -> set[str]:
        """Direcciones de recursos con algún cambio real (todo menos no-op).

        Usado por `shadowstack sync` para excluir estos recursos del pull
        inicial desde AWS real y no contaminar el gemelo antes de simular.
        """
        return {c.address for c in self.resource_changes if c.action != ChangeAction.NO_OP}


def parse_plan_dict(raw: dict[str, Any]) -> PlanDiff:
    """Construye un PlanDiff a partir del dict ya deserializado de un plan.json."""
    resource_changes = [
        ResourceChange(
            address=rc["address"],
            resource_type=rc["type"],
            name=rc["name"],
            provider_name=rc.get("provider_name", ""),
            action=_action_from_raw(rc["change"]["actions"]),
            before=rc["change"].get("before"),
            after=rc["change"].get("after"),
        )
        for rc in raw.get("resource_changes", [])
    ]
    return PlanDiff(terraform_version=raw.get("terraform_version"), resource_changes=resource_changes)


def parse_plan(path: str | Path) -> PlanDiff:
    """Lee y parsea un plan.json de Terraform desde disco."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_plan_dict(raw)
