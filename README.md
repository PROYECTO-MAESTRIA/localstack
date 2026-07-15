# ShadowStack

> Un gemelo digital para infraestructura cloud en AWS — sincroniza, simula y detecta riesgos antes de llegar a producción.

ShadowStack replica tu infraestructura real de AWS en un entorno local con [LocalStack](https://localstack.cloud/), aplica los cambios de Terraform propuestos sobre la réplica, y ejecuta un agente de IA (con LangGraph) que analiza los logs y eventos resultantes para producir un reporte de riesgos — sin tocar tu cuenta de producción.

---

## Cómo funciona

```
Tus archivos .tf (modificados)
        │
        ▼
  terraform plan          ← identifica qué recursos van a cambiar
        │
        ▼
  shadowstack sync        ← lee el estado real de AWS y replica todo
        │                    EXCEPTO los recursos en el diff
        ▼
  shadowstack apply       ← aplica solo los cambios propuestos en LocalStack
        │
        ▼
  shadowstack report      ← el agente lee los logs, clasifica riesgos
                             y produce un reporte estructurado
```

---

## Arquitectura

<img width="500" alt="image" src="https://github.com/user-attachments/assets/c1bc1138-6b5a-4334-be73-0ac2f1e36265" />


El sistema tiene cuatro componentes principales:

| Componente | Descripción |
|---|---|
| **Sync Engine** | Lee el estado de Lambda, API Gateway y DynamoDB desde AWS y lo replica en LocalStack, omitiendo los recursos marcados en el plan de Terraform |
| **Diff Parser** | Parsea el `plan.json` de Terraform para extraer el conjunto de recursos que serán modificados, creados o eliminados |
| **Entorno LocalStack** | Fork de LocalStack configurado para emular Lambda, API Gateway y DynamoDB en el entorno experimental |
| **Agente LangGraph** | Agente multi-nodo que ingiere logs y eventos del run en LocalStack, clasifica tipos de riesgo y genera un reporte estructurado con advertencias y recomendaciones |

---

## Alcance del prototipo

Este prototipo se enfoca en tres servicios de AWS:

- **AWS Lambda** — configuración de funciones, memoria, timeout, runtime
- **Amazon API Gateway** — rutas, integraciones, autorización
- **Amazon DynamoDB** — esquema de tablas, modo de facturación, capacidad, índices


Fuera del alcance de este prototipo: datos de costo en tiempo real, modelado de tráfico de usuarios, servicios fuera de los tres anteriores.

---

## Referencia del CLI

ShadowStack se opera mediante un CLI construido con [Typer](https://typer.tiangolo.com/).

```bash
# Sincronizar el estado de AWS en LocalStack (excluyendo los recursos del plan)
shadowstack sync --plan plan.json

# Aplicar los cambios de Terraform propuestos sobre LocalStack
shadowstack apply --plan plan.json

# Ejecutar el agente LangGraph y producir el reporte de riesgos
shadowstack report --output reporte.md

# Ejecutar el pipeline completo en un solo comando
shadowstack run --plan plan.json --output reporte.md
```

---

## Inicio rápido

### Requisitos previos

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [Docker](https://www.docker.com/) (requerido por LocalStack)
- Credenciales de AWS configuradas (`aws configure`) — acceso de solo lectura es suficiente para el paso de sincronización
- Licencia de LocalStack Pro o Community (ver [localstack.cloud](https://localstack.cloud/))

---

## Casos de prueba

Se incluyen dos casos de prueba base en `infra/` para validar la capacidad de detección de riesgos del agente.

### Caso 01 — Reducción de memoria en Lambda

**Cambio:** `memory_size` reducida de 512 MB a 128 MB en una Lambda que procesa archivos.  
**Riesgo esperado:** El agente detecta errores de out-of-memory en los logs de LocalStack y advierte que la reducción de memoria puede causar fallos bajo cargas de trabajo reales.

```bash
cd infra/caso_01_lambda_memoria
terraform plan -out=plan.tfplan && terraform show -json plan.tfplan > plan.json
shadowstack run --plan plan.json --output reporte.md
```

### Caso 02 — Cambio de modo de facturación en DynamoDB

**Cambio:** Modo de facturación de la tabla cambiado de `PAY_PER_REQUEST` a `PROVISIONED` con `read_capacity = 1` y `write_capacity = 1`.  
**Riesgo esperado:** El agente detecta eventos `ProvisionedThroughputExceededException` y advierte que la capacidad provisionada es insuficiente para el volumen de escrituras observado.

```bash
cd infra/caso_02_dynamo_facturacion
terraform plan -out=plan.tfplan && terraform show -json plan.tfplan > plan.json
shadowstack run --plan plan.json --output reporte.md
```

---

## Formato del reporte de riesgos (Boceto inicial)

El agente produce un reporte estructurado en markdown con las siguientes secciones:

```markdown
# Reporte de riesgos — ShadowStack

## Resumen
- Recursos analizados: N
- Riesgos detectados: N
- Nivel de riesgo general: ALTO / MEDIO / BAJO

## Riesgos detectados

### [ALTO] Memoria insuficiente en Lambda — nombre-funcion
**Recurso:** aws_lambda_function.procesar_archivos  
**Cambio:** memory_size 512 → 128  
**Evidencia:** Error de out-of-memory en log de ejecución (timestamp)  
**Recomendación:** Mantener memory_size ≥ 256 MB para cargas de trabajo con procesamiento de archivos.

## Cambios seguros
- (lista de cambios que no produjeron errores ni advertencias)
```

---

## Contexto de investigación

ShadowStack se desarrolla como parte de una tesis de maestría en la **Escuela Colombiana de Ingeniería Julio Garavito** (Maestría en Informatica con enfasis en Ingenieria de software avanzado), en el marco del proyecto:

> *"Prototipo de gemelo digital para infraestructura cloud en AWS con agente de IA: sincronización basada en observabilidad para simulación segura de cambios y análisis predictivo de riesgos"*

El prototipo sirve como fundamento práctico para la investigación sobre gemelos digitales y análisis predictivo de riesgos en infraestructura cloud.
