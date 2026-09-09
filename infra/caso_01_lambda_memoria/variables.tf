variable "aws_region" {
  description = "Región de AWS donde se despliega el caso de prueba"
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "Profile de AWS CLI a usar para desplegar este caso (necesita permisos de escritura sobre Lambda/IAM; distinto del profile de solo lectura que usa ShadowStack para leer estado). Ignorado si use_localstack = true."
  type        = string
  default     = null
}

variable "use_localstack" {
  description = "Si es true, este mismo código crea los recursos en el gemelo digital (LocalStack, http://localhost:4566) en vez de en AWS real. Es el mismo mecanismo que usará `shadowstack apply`."
  type        = bool
  default     = true
}

variable "function_name" {
  description = "Nombre de la función Lambda del caso de prueba"
  type        = string
  default     = "shadowstack-caso01-memoria"
}

variable "memory_size" {
  description = "Memoria asignada a la Lambda (MB). Súbela y corre `terraform plan` para generar el diff que ShadowStack va a simular."
  type        = number
  default     = 128
}
