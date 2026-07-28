Ya tengo el panorama completo. Este proyecto es el prototipo de una **tesis de maestría** (Escuela Colombiana de Ingeniería Julio Garavito, autores Enrique González Suárez y Sergio Andrés Otero Herrera) llamado **ShadowStack**.

## Idea general

ShadowStack busca crear un **"gemelo digital" de una infraestructura AWS real**, corriendo localmente en **LocalStack**, para poder simular cambios de infraestructura (por ejemplo, los que propone un `terraform plan`) de forma segura, y luego analizar el riesgo de esos cambios con un **agente de IA (Claude vía LangGraph)** antes de aplicarlos en producción de verdad.

## Estructura del repo

```
shadowstack/
├── docker-compose.yml        # levanta LocalStack
├── pyproject.toml            # dependencias + entry point del CLI
├── shadowstack/
│   ├── cli.py                # CLI (Typer) — el archivo que tienes abierto
│   ├── config.py             # clientes boto3 (LocalStack y AWS real)
│   ├── agent/                # vacío (futuro agente LangGraph)
│   ├── report/                # vacío (futuro generador de reportes)
│   └── sync/                  # vacío (futuro parser de diff + motor de sync)
└── tests/test_localstack_connectivity.py
```

## El CLI (`cli.py`) — 5 comandos planeados, solo 1 implementado

El comando de consola es `shadowstack` (registrado en `pyproject.toml`). El flujo pensado es:

1. **`shadowstack doctor`** ✅ *(único comando funcional hoy)*
   Verifica que LocalStack esté arriba y que boto3 pueda hablar con los 3 servicios "en scope" del prototipo: `lambda`, `apigateway`, `dynamodb`. Imprime una tabla OK/FALLO. Es el chequeo de salud del entorno — se corre justo después de `docker compose up -d` y antes de usar cualquier otro comando.

2. **`shadowstack sync --plan plan.json [--full]`** ⏳ *(placeholder)*
   Idea futura: leer el `plan.json` de Terraform, consultar el estado real de AWS (vía `real_aws_client()`), y replicarlo en LocalStack — excluyendo por defecto los recursos que el diff va a cambiar, para no "contaminar" el gemelo antes de simular.

3. **`shadowstack apply --plan plan.json`** ⏳ *(placeholder)*
   Idea futura: aplicar el cambio propuesto por Terraform dentro del gemelo (LocalStack), simulando el efecto sin tocar AWS real.

4. **`shadowstack report --output reporte.md`** ⏳ *(placeholder)*
   Idea futura: invocar el agente LangGraph para analizar el resultado de la simulación y generar un reporte de riesgos en Markdown.

5. **`shadowstack run --plan plan.json --output reporte.md`** ⏳ *(placeholder)*
   El orquestador: encadenaría sync → apply → report en un solo pipeline.

Hoy, `sync`, `apply`, `report` y `run` solo imprimen "Aún no implementado" — son stubs que documentan la interfaz futura vía Typer, pero sin lógica real.

## `config.py` — el corazón de la conexión dual

Este es el único módulo de soporte con lógica real, y materializa la idea de "gemelo digital":

- **`localstack_client(service_name)`**: cliente boto3 apuntando al LocalStack local (`http://localhost:4566`), con credenciales dummy. Solo permite servicios de una whitelist (`lambda`, `apigateway`, `dynamodb`, `cloudwatch`, `logs`) — pedir otro (ej. `s3`) lanza `ValueError`. Este es el cliente que usa `doctor`.
- **`real_aws_client(service_name)`**: cliente boto3 apuntando a la cuenta AWS real (usando un profile de solo lectura definido en `.env`). Pensado para ser usado por el futuro Sync Engine, que leerá el estado real para replicarlo en el gemelo.

## Infraestructura auxiliar

- **`docker-compose.yml`**: levanta LocalStack con los servicios `lambda,apigateway,dynamodb,cloudwatch,logs,iam,sts` (iam/sts como soporte interno aunque no estén en la whitelist de boto3), con `LAMBDA_EXECUTOR=docker` para poder ejecutar Lambdas reales dentro del gemelo.
- **`tests/test_localstack_connectivity.py`**: smoke test marcado `requires_localstack` que valida la conectividad de `doctor` y el comportamiento de la whitelist.
- **`infra/caso_01_lambda_memoria/` y `caso_02_dynamo_facturacion/`**: carpetas vacías reservadas para futuros casos de prueba en Terraform (nombres sugieren "Lambda con problema de memoria" y "facturación con DynamoDB").

## En resumen

Todo lo "ejecutable" hoy se reduce a: `docker compose up -d` → `shadowstack doctor` → tests de conectividad. El resto (parser de diffs de Terraform, motor de sincronización, agente LangGraph, generador de reportes) son carpetas vacías que reservan la arquitectura para las siguientes fases del cronograma de la tesis (agosto-septiembre, según el README).

¿Quieres que profundice en alguna parte específica (por ejemplo, el diseño que tendría el Sync Engine, o cómo se integraría el agente LangGraph)?

---

# Informe de exploración: proyecto ShadowStack

## 1. Qué es el proyecto

**Ubicación:** `e:\U\Maestria\Tesis\pruebas\shadowstack`

Es el prototipo de una **tesis de maestría** (Escuela Colombiana de Ingeniería Julio Garavito), descrito en `README.md` (líneas 1-7) y `pyproject.toml` (líneas 1-10, autores: Enrique González Suárez y Sergio Andrés Otero Herrera).

**Propósito (según `pyproject.toml:4-5` y `README.md:3-5`):** construir un **"gemelo digital" (digital twin) de infraestructura cloud en AWS**, con un agente de IA, que permite:
- Sincronizar el estado de una cuenta AWS real hacia un entorno AWS emulado localmente (LocalStack), basándose en observabilidad.
- Simular de forma segura cambios de infraestructura (p. ej. cambios propuestos por Terraform) sin tocar producción.
- Hacer análisis predictivo de riesgos sobre esos cambios, usando un agente LLM (LangGraph + Claude).

En otras palabras: es una herramienta pensada para tomar un `plan.json` de Terraform (el diff de cambios de infraestructura), replicar el estado real de AWS en un "gemelo" corriendo en LocalStack, aplicar ahí el cambio propuesto, observarlo, y generar un reporte de riesgos con IA — todo antes de aplicar el cambio en producción real.

**Estado actual del proyecto: es un prototipo muy temprano.** Solo está implementado el comando de diagnóstico (`doctor`); todo lo demás (sync, apply, report, run) son *stubs* (placeholders) que solo imprimen "Aún no implementado". Los módulos `agent/`, `report/` y `sync/` existen como paquetes pero sus `__init__.py` están **vacíos** — es decir, aún no contienen lógica.

## 2. Estructura completa del repositorio

```
shadowstack/
├── .env.example                          # plantilla de variables de entorno
├── .gitignore
├── README.md
├── docker-compose.yml                    # levanta LocalStack
├── pyproject.toml                        # metadata, dependencias, entry point CLI
├── pytest.ini                            # marker "requires_localstack"
├── infra/
│   ├── caso_01_lambda_memoria/.gitkeep   # carpeta vacía (futuro caso de prueba Terraform)
│   └── caso_02_dynamo_facturacion/.gitkeep  # carpeta vacía (futuro caso de prueba Terraform)
├── shadowstack/                          # paquete Python principal
│   ├── __init__.py                       # vacío
│   ├── cli.py                            # CLI Typer — único módulo con lógica real
│   ├── config.py                         # clientes boto3 (LocalStack y AWS real)
│   ├── agent/__init__.py                 # vacío (futuro agente LangGraph)
│   ├── report/__init__.py                # vacío (futuro formateador de reportes)
│   └── sync/__init__.py                  # vacío (futuro Diff Parser + Sync Engine)
└── tests/
    ├── __init__.py
    └── test_localstack_connectivity.py   # smoke test de conectividad boto3 ↔ LocalStack
```

No hay carpeta `docs/`. La única documentación de arquitectura es el `README.md` y los comentarios/docstrings dentro de `cli.py` y `config.py`.

## 3. `shadowstack/cli.py` — comandos CLI (Typer)

Archivo completo, 99 líneas. Define una app Typer (`app = typer.Typer(...)`, línea 21) expuesta como comando de consola `shadowstack` vía `pyproject.toml:36` (`shadowstack = "shadowstack.cli:app"`).

El docstring inicial (líneas 4-11) documenta la interfaz **prevista** a futuro:
```
shadowstack sync --plan plan.json
shadowstack apply --plan plan.json
shadowstack report --output reporte.md
shadowstack run --plan plan.json --output reporte.md
```

### `doctor` (líneas 25-57) — ÚNICO comando funcional hoy
- Sin argumentos.
- Verifica que LocalStack esté arriba y que boto3 pueda comunicarse con los 3 servicios "en scope" del prototipo: `lambda` (`list_functions`), `apigateway` (`get_rest_apis`), `dynamodb` (`list_tables`).
- Construye un cliente por servicio con `localstack_client(service_name)` (de `config.py`) y ejecuta la llamada de prueba correspondiente.
- Imprime una tabla Rich con estado OK/FALLO por servicio y el detalle del error (primeros 80 caracteres) si falla.
- Si algún servicio falla, sale con código 1 (`typer.Exit(code=1)`); si todo va bien imprime "Entorno LocalStack funcional."
- **Cuándo usarlo:** paso de verificación de entorno, después de `docker compose up -d`, antes de usar cualquier otro comando. Es literalmente el entregable de la "semana 1" mencionado en el README (líneas 39-43).

### `sync` (líneas 60-69) — placeholder, no implementado
- Opciones: `--plan` (ruta a `plan.json` de Terraform, obligatorio) y `--full` (booleano, default False).
- Docstring: "Sincroniza AWS real → LocalStack (excluyendo por defecto los recursos del diff)".
- Actualmente solo imprime un mensaje amarillo "Aún no implementado — sub-bloque A/B, semanas 2-5" junto con los valores recibidos. No ejecuta ninguna lógica de sincronización real todavía.

### `apply` (líneas 72-77) — placeholder, no implementado
- Opción: `--plan` (ruta al `plan.json`, obligatorio).
- Docstring: "Aplica el cambio propuesto en LocalStack".
- Solo imprime "Aún no implementado."

### `report` (líneas 80-85) — placeholder, no implementado
- Opción: `--output` (ruta de salida, default `"reporte.md"`).
- Docstring: "Genera el reporte de riesgos con el agente LangGraph".
- Solo imprime "Aún no implementado — Fase 4."

### `run` (líneas 88-94) — placeholder, no implementado
- Opciones: `--plan` (obligatorio) y `--output` (default `"reporte.md"`).
- Docstring: "Pipeline completo: sync → apply → report" — es decir, el comando orquestador que en el futuro encadenará los tres pasos anteriores.
- Solo imprime "Aún no implementado."

## 4. `shadowstack/config.py` — cliente boto3 central

Único módulo de soporte real usado por `cli.py`. Resumen:

- `load_dotenv()` (línea 14) carga variables desde `.env`.
- `LOCALSTACK_ENDPOINT` (línea 16): default `http://localhost:4566`.
- `LOCALSTACK_REGION` (línea 17): default `us-east-1`.
- `LOCALSTACK_SERVICES` (línea 20): lista blanca de servicios permitidos en el gemelo: `["lambda", "apigateway", "dynamodb", "cloudwatch", "logs"]`.
- `_localstack_session()` (líneas 23-28): crea una `boto3.Session` con credenciales dummy (`test`/`test`) apuntando a LocalStack.
- `localstack_client(service_name)` (líneas 31-42, cacheado con `@lru_cache`): devuelve un cliente boto3 apuntando a `LOCALSTACK_ENDPOINT`. Si `service_name` no está en `LOCALSTACK_SERVICES`, lanza `ValueError`. Este es el cliente que usa `doctor` en `cli.py`.
- `real_aws_client(service_name)` (líneas 45-56, también cacheado): crea un cliente boto3 apuntando a **AWS real**, usando el profile de `AWS_REAL_PROFILE` y región `AWS_REAL_REGION`. El docstring aclara que está pensado para ser usado por el futuro `aws_reader.py` del Sync Engine (todavía no existe como archivo).

Nótese que `config.py` es el único punto donde se materializa la idea de "gemelo digital": un cliente habla con LocalStack (el gemelo) y otro con AWS real (la fuente de verdad a replicar).

## 5. Módulos vacíos (arquitectura planeada, aún sin código)

Estos tres paquetes existen físicamente pero sus `__init__.py` están vacíos — no hay funciones ni clases que reportar todavía. Su rol futuro, según el README y los docstrings de `cli.py`/`config.py`:

- **`shadowstack/sync/`** — "Diff Parser + Sync Engine" (README línea 63). Previsto para semanas 2-3: parsear el `plan.json` de Terraform (diff de cambios) y sincronizar el estado de AWS real hacia LocalStack, típicamente mediante módulos futuros `diff_parser.py`, `aws_reader.py` y `localstack_writer.py` (mencionados en la tabla de cronograma del README, líneas 74-80), excluyendo por defecto los recursos que van a cambiar (para no "contaminar" la simulación).
- **`shadowstack/agent/`** — "Agente LangGraph" (README línea 64), previsto para la Fase 4. Usará `langgraph`, `langchain-core` y `langchain-anthropic` (dependencias declaradas en `pyproject.toml:16-18`) junto con el modelo configurado en `.env` (`LANGGRAPH_MODEL=claude-sonnet-4-6`, `.env.example:15`) para hacer el análisis predictivo de riesgos.
- **`shadowstack/report/`** — "Formateo del reporte de riesgos" (README línea 64). Generará el `reporte.md` de salida que consumirán los comandos `report`/`run`.

No hay ningún "tool" externo de análisis estático de seguridad (tipo Semgrep, Checkov, tfsec, etc.) integrado todavía — el proyecto es, en esta etapa, exclusivamente infraestructura de conectividad boto3 + CLI base. No confundir con herramientas típicas de "scanner de vulnerabilidades": el dominio aquí es simulación de infraestructura cloud (Terraform + AWS + LocalStack), no análisis de código.

## 6. Configuración, infraestructura auxiliar y tests

- **`docker-compose.yml`**: levanta un único contenedor `shadowstack-localstack` (imagen `localstack/localstack:latest`), exponiendo el puerto 4566 (gateway edge de todos los servicios) y el rango 4510-4559. Variable `SERVICES=lambda,apigateway,dynamodb,cloudwatch,logs,iam,sts` (más servicios de los que boto3 tiene permitidos en `config.py`, ya que iam/sts se necesitan como soporte interno aunque no estén en la whitelist de `LOCALSTACK_SERVICES`). Usa `PERSISTENCE=1` y monta el socket de Docker para poder ejecutar Lambdas (`LAMBDA_EXECUTOR=docker`). Tiene healthcheck contra `/_localstack/health`.
- **`.env.example`**: plantilla con: endpoint/credenciales dummy de LocalStack, `AWS_REAL_PROFILE`/`AWS_REAL_REGION` (perfil de solo lectura para leer AWS real), `ANTHROPIC_API_KEY` y `LANGGRAPH_MODEL` (para el futuro agente), y `LOG_LEVEL`.
- **`pytest.ini`**: define el marker `requires_localstack` para pruebas de integración que necesitan LocalStack corriendo.
- **`tests/test_localstack_connectivity.py`**: smoke test (todo marcado `requires_localstack`) que:
  - Verifica que `localstack_client("lambda").list_functions()` responde con clave `"Functions"`.
  - Verifica que `localstack_client("apigateway").get_rest_apis()` responde con clave `"items"`.
  - Verifica que `localstack_client("dynamodb").list_tables()` responde con clave `"TableNames"`.
  - Verifica que pedir un servicio fuera de scope (`"s3"`) lanza `ValueError` — esto documenta el comportamiento real de la whitelist en `config.py`.
  - Se pueden correr con `pytest -m requires_localstack -v` (con Docker arriba) o excluir con `pytest -m "not requires_localstack" -v`.
- **`infra/caso_01_lambda_memoria/` e `infra/caso_02_dynamo_facturacion/`**: carpetas vacías (solo `.gitkeep`) reservadas para futuros casos de prueba en Terraform (nombres sugieren un caso de "Lambda con problema de memoria" y otro de "facturación con DynamoDB"), que servirán como escenarios de ejemplo para probar el pipeline sync→apply→report.

## 7. Flujo/arquitectura en palabras (diseño previsto vs. lo implementado)

**Flujo diseñado (aún no codificado, solo documentado en docstrings/README):**
1. El usuario tiene un `plan.json` generado por `terraform plan -out=... && terraform show -json`.
2. `shadowstack sync --plan plan.json` leería ese plan (Diff Parser en `sync/`), consultaría el estado real de AWS vía `real_aws_client()` (`aws_reader.py` futuro) y replicaría ese estado en LocalStack vía `localstack_writer.py` futuro, excluyendo los recursos que el diff va a modificar (para no pre-contaminar el gemelo con el cambio que aún no se ha simulado).
3. `shadowstack apply --plan plan.json` aplicaría el cambio propuesto por Terraform dentro del gemelo (LocalStack), simulando el efecto sin tocar AWS real.
4. `shadowstack report --output reporte.md` invocaría el agente LangGraph (`agent/`) para analizar el resultado de la simulación (posiblemente con métricas de CloudWatch, mencionado en el cronograma) y generar un reporte de riesgos (`report/`) en Markdown.
5. `shadowstack run --plan plan.json --output reporte.md` encadenaría los tres pasos anteriores en un solo pipeline.

**Lo único realmente ejecutable hoy** es:
1. `docker compose up -d` levanta LocalStack.
2. `shadowstack doctor` valida que boto3 puede hablar con lambda/apigateway/dynamodb en ese LocalStack.
3. Los tests de conectividad (`pytest -m requires_localstack`) confirman lo mismo de forma automatizada.

## Resumen para explicar al usuario

Es el **esqueleto inicial de una tesis** que busca construir un "gemelo digital" de AWS (usando LocalStack) para simular cambios de infraestructura Terraform de forma segura y analizarlos con un agente de IA (Claude vía LangGraph) antes de aplicarlos en producción. Hoy en día, de los 5 comandos CLI planeados (`doctor`, `sync`, `apply`, `report`, `run`), **solo `doctor` está implementado** — sirve para comprobar que el entorno LocalStack (Lambda, API Gateway, DynamoDB) responde correctamente vía boto3. El resto son stubs que imprimen "Aún no implementado". No hay todavía ningún parser de diffs de Terraform, ningún motor de sincronización, ningún agente LangGraph ni generador de reportes — esos tres subsistemas (`sync/`, `agent/`, `report/`) existen como carpetas de paquete vacías, reservando la arquitectura para las siguientes fases del cronograma indicado en el propio README (agosto-septiembre).
