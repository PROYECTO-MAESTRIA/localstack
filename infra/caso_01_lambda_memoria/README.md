# Caso 01 — Lambda con problema de memoria

Caso de prueba mínimo: una función Lambda desplegada con poca memoria
(`memory_size = 128`), que luego se sube para generar un `plan.json` real
con el que probar el resto del pipeline de ShadowStack (`diff_parser`,
y más adelante `sync`/`apply`/`report`).

Requiere un profile de AWS CLI con permisos de **escritura** (Lambda, IAM) —
distinto del profile de solo lectura que usa ShadowStack (`AWS_REAL_PROFILE`
en `.env`) para leer el estado real.

## 1. Desplegar el estado base (memoria baja)

```bash
cd infra/caso_01_lambda_memoria
terraform init
terraform apply -var="aws_profile=<tu-profile-con-permisos-de-escritura>"
```

Esto crea la Lambda en tu cuenta real de AWS con `memory_size = 128`.

## 2. Generar el cambio a simular

Sube el valor de memoria y pide un plan (sin aplicarlo):

```bash
terraform plan -var="aws_profile=<tu-profile>" -var="memory_size=512" -out=tfplan
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
terraform destroy -var="aws_profile=<tu-profile>"
```
