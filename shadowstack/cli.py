"""
CLI de ShadowStack (Typer).

Comandos previstos (sección 3.1 del documento de contexto):
    shadowstack sync                    # pull completo (bootstrap del gemelo)
    shadowstack sync --plan plan.json
    shadowstack apply --plan plan.json
    shadowstack report --output reporte.md
    shadowstack run --plan plan.json --output reporte.md

Por ahora solo se implementa `doctor`, para validar que el entorno LocalStack
está funcional antes de construir el resto del pipeline (entregable semana 1).
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from shadowstack.config import LOCALSTACK_ENDPOINT, localstack_client
from shadowstack.sync.aws_reader import read_lambda_functions
from shadowstack.sync.diff_parser import parse_plan
from shadowstack.sync.localstack_writer import write_lambda_function

app = typer.Typer(help="ShadowStack — gemelo digital para infraestructura AWS")
console = Console()


@app.command()
def doctor() -> None:
    """
    Valida que el entorno LocalStack está arriba y que boto3 puede hablar
    con Lambda, API Gateway y DynamoDB (los tres servicios en scope).
    """
    checks = [
        ("lambda", lambda c: c.list_functions()),
        ("apigateway", lambda c: c.get_rest_apis()),
        ("dynamodb", lambda c: c.list_tables()),
    ]

    table = Table(title=f"ShadowStack doctor — endpoint: {LOCALSTACK_ENDPOINT}")
    table.add_column("Servicio")
    table.add_column("Estado")
    table.add_column("Detalle")

    all_ok = True
    for service_name, check_fn in checks:
        try:
            client = localstack_client(service_name)
            check_fn(client)
            table.add_row(service_name, "[green]OK[/green]", "Responde correctamente")
        except Exception as exc:  # noqa: BLE001 — queremos capturar y reportar cualquier fallo
            all_ok = False
            table.add_row(service_name, "[red]FALLO[/red]", str(exc)[:80])

    console.print(table)

    if not all_ok:
        raise typer.Exit(code=1)

    console.print("\n[bold green]Entorno LocalStack funcional.[/bold green]")


@app.command()
def sync(
    plan: str | None = typer.Option(
        None,
        "--plan",
        help="Ruta al plan.json de Terraform. Si se omite, se hace un pull completo "
        "(bootstrap del gemelo), equivalente a pasar --full.",
    ),
    full: bool = typer.Option(
        False, "--full", help="Sincroniza toda la infraestructura, ignorando la exclusión del diff"
    ),
) -> None:
    """Sincroniza AWS real → LocalStack (excluyendo por defecto los recursos del diff)."""
    if plan is None:
        full = True

    excluded_function_names: set[str] = set()
    if not full:
        diff = parse_plan(plan)
        for change in diff.resource_changes:
            if change.resource_type != "aws_lambda_function" or change.address not in diff.changed_addresses:
                continue
            attrs = change.after or change.before or {}
            if attrs.get("function_name"):
                excluded_function_names.add(attrs["function_name"])

    console.print("[dim]Leyendo funciones Lambda de AWS real...[/dim]")
    functions = read_lambda_functions()

    table = Table(title="shadowstack sync — Lambda")
    table.add_column("Función")
    table.add_column("Acción")

    for state in functions:
        if state.function_name in excluded_function_names:
            table.add_row(state.function_name, "[yellow]excluida (parte del diff)[/yellow]")
            continue
        write_lambda_function(state)
        table.add_row(state.function_name, "[green]sincronizada[/green]")

    console.print(table)
    console.print(
        "\n[dim]Nota: por ahora solo sincroniza Lambda. apigateway/dynamodb aún no están conectados.[/dim]"
    )


@app.command()
def apply(
    plan: str = typer.Option(..., "--plan", help="Ruta al plan.json de Terraform"),
) -> None:
    """Aplica el cambio propuesto en LocalStack."""
    console.print("[yellow]Aún no implementado.[/yellow]")


@app.command()
def report(
    output: str = typer.Option("reporte.md", "--output", help="Ruta de salida del reporte"),
) -> None:
    """Genera el reporte de riesgos con el agente LangGraph."""
    console.print("[yellow]Aún no implementado — Fase 4.[/yellow]")


@app.command()
def run(
    plan: str = typer.Option(..., "--plan", help="Ruta al plan.json de Terraform"),
    output: str = typer.Option("reporte.md", "--output", help="Ruta de salida del reporte"),
) -> None:
    """Pipeline completo: sync → apply → report."""
    console.print("[yellow]Aún no implementado.[/yellow]")


if __name__ == "__main__":
    app()
