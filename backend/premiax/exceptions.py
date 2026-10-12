from rest_framework import status
from rest_framework.exceptions import APIException


class ReglaDeNegocio(APIException):
    """Error 400 con un mensaje legible: la API responde {"detail": "..."}."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La operación no está permitida.'
    default_code = 'regla_negocio'
