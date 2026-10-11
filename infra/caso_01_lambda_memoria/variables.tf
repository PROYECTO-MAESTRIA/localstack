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
  description = "true = crea los recursos en el gemelo digital (LocalStack); false = crea en AWS real. SIN DEFAULT A PROPÓSITO: pasarlo siempre explícito con -var, para no aplicar por accidente contra el destino equivocado (ver README, sección 5 vs. secciones 1-4)."
  type        = bool
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
