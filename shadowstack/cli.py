"""
CLI de ShadowStack (Typer).

Comandos previstos (sección 3.1 del documento de contexto):
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
    plan: str = typer.Option(..., "--plan", help="Ruta al plan.json de Terraform"),
    full: bool = typer.Option(
        False, "--full", help="Sincroniza toda la infraestructura, ignorando la exclusión del diff"
    ),
) -> None:
    """Sincroniza AWS real → LocalStack (excluyendo por defecto los recursos del diff)."""
    console.print("[yellow]Aún no implementado — sub-bloque A/B, semanas 2-5.[/yellow]")
    console.print(f"plan={plan} full={full}")


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
