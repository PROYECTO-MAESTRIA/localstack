variable "aws_region" {
  description = "Región de AWS donde se despliega el caso de prueba"
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "Profile de AWS CLI a usar para desplegar este caso (necesita permisos de escritura sobre Lambda/IAM; distinto del profile de solo lectura que usa ShadowStack para leer estado)"
  type        = string
  default     = null
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
