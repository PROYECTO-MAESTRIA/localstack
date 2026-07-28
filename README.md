# ShadowStack

Gemelo digital para infraestructura cloud en AWS con agente de IA: sincronización
basada en observabilidad para simulación segura de cambios y análisis predictivo
de riesgos.

Tesis de Maestría — Escuela Colombiana de Ingeniería Julio Garavito.

## Estado actual (Fase 2, sub-bloque A — semana 1)

✅ Setup del repo base
✅ `docker-compose.yml` para levantar LocalStack
✅ Validación de conectividad boto3 → LocalStack (Lambda / API Gateway / DynamoDB)

## Requisitos

- Python 3.11+
- Docker y Docker Compose
- (Opcional para esta semana) Terraform >= 1.5

## Setup

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Crear entorno virtual e instalar dependencias
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. Levantar LocalStack
docker compose up -d

# 4. Esperar a que el healthcheck pase (o revisar manualmente)
curl http://localhost:4566/_localstack/health

# 5. Validar que boto3 responde en los servicios en scope
shadowstack doctor
```

Si `shadowstack doctor` reporta `OK` en `lambda`, `apigateway` y `dynamodb`,
el entorno LocalStack está funcional (entregable de la semana 27 jul – 2 ago).

## Tests

```bash
# Con LocalStack corriendo:
pytest -m requires_localstack -v

# Sin Docker (skip de pruebas de integración):
pytest -m "not requires_localstack" -v
```

## Estructura del repositorio

```
shadowstack/
├── shadowstack/
│   ├── cli.py                  # CLI (Typer): sync / apply / report / run / doctor
│   ├── config.py                # Clientes boto3 (LocalStack y AWS real)
│   ├── sync/                    # Diff Parser + Sync Engine (semanas 2-3)
│   ├── agent/                   # Agente LangGraph (Fase 4)
│   └── report/                  # Formateo del reporte de riesgos
├── infra/                       # Casos de prueba (Terraform)
├── tests/
├── docker-compose.yml
├── .env.example
└── pyproject.toml
```

## Próximos pasos (cronograma Fase 2)

| Semana | Entregable |
|---|---|
| 3–9 ago | `diff_parser.py` + tests sobre `plan.json` |
| 10–16 ago | `aws_reader.py` + `localstack_writer.py` (Sync Engine end-to-end) |
| 17–23 ago | Módulo de métricas CloudWatch |
| 24–30 ago | `shadowstack sync` con flag de pull completo |
| 31 ago–13 sep | Métrica de fidelidad + cierre de Fase 2 |
