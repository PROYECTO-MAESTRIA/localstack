# Caso 01 — Lambda con problema de memoria

Caso de prueba mínimo: una función Lambda desplegada con poca memoria
(`memory_size = 128`), que luego se sube para generar un `plan.json` real
con el que probar el resto del pipeline de ShadowStack (`diff_parser`,
y más adelante `sync`/`apply`/`report`).

Requiere un profile de AWS CLI con permisos de **escritura** (Lambda, IAM) —
distinto del profile de solo lectura que usa ShadowStack (`AWS_REAL_PROFILE`
en `.env`) para leer el estado real.

> `use_localstack` no tiene default a propósito — SIEMPRE pásalo explícito
> (`true` o `false`) en cada `plan`/`apply`/`destroy`. Omitirlo es un error
> de Terraform, no un accidente silencioso hacia el destino equivocado.

## 1. Desplegar el estado base (memoria baja)

```bash
cd infra/caso_01_lambda_memoria
terraform workspace select default   # AWS real
terraform init
terraform apply -var="use_localstack=false" -var="aws_profile=<tu-profile-con-permisos-de-escritura>"
```

Esto crea la Lambda en tu cuenta real de AWS con `memory_size = 128`.

## 2. Generar el cambio a simular

Sube el valor de memoria y pide un plan (sin aplicarlo):

```bash
terraform plan -var="use_localstack=false" -var="aws_profile=<tu-profile>" -var="memory_size=512" -out=tfplan
terraform show -json tfplan > ../../plan.json
```

`plan.json` queda en la raíz del repo (ya está en `.gitignore`, no se commitea).

## 3. Usarlo con ShadowStack

```bash
cd ../..
python -c "from shadowstack.sync.diff_parser import parse_plan; d = parse_plan('plan.json'); print(d.to_update)"
```

Deberías ver el cambio de `aws_lambda_function.memoria` con
`before={'memory_size': 128, ...}` y `after={'memory_size': 512, ...}`.

## 4. Limpieza

Cuando termines de probar, destruye el recurso para no dejar nada corriendo
en tu cuenta real:

```bash
terraform destroy -var="use_localstack=false" -var="aws_profile=<tu-profile>"
```

## 5. Crear la misma Lambda en el gemelo digital (LocalStack)

Este mismo código puede crear los recursos en LocalStack en vez de AWS real,
usando `use_localstack=true` — es el mecanismo que usará `shadowstack apply`
para simular cambios sin tocar producción.

Como el workspace `default` ya tiene el estado de la Lambda real, usamos un
**workspace de Terraform separado** para no mezclar los dos estados:

```bash
# Requiere LocalStack corriendo: docker compose up -d (desde la raíz del repo)
terraform workspace new localstack   # solo la primera vez
terraform workspace select localstack

terraform apply -var="use_localstack=true"
```

No hace falta `aws_profile` (se ignora) ni credenciales reales — usa las
credenciales dummy `test`/`test`, igual que boto3 en `config.py`.

Para verificar que la Lambda quedó en el gemelo:

```bash
cd ../..
python -c "from shadowstack.config import localstack_client; print(localstack_client('lambda').list_functions()['Functions'])"
```

Para volver a trabajar con el estado de AWS real:

```bash
terraform workspace select default
```
