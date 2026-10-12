"""Validación de archivos subidos (RNF-009): extensión, tamaño máximo de 10 MB y tipo real del contenido."""
import os

from PIL import Image
from rest_framework import serializers

MAX_BYTES = 10 * 1024 * 1024

# Firmas ("magic bytes") por extensión permitida para documentos.
_FIRMAS_DOCUMENTO = {
    '.pdf': (b'%PDF',),
    '.doc': (b'\xd0\xcf\x11\xe0',),
    '.docx': (b'PK\x03\x04',),
    '.odt': (b'PK\x03\x04',),
}
EXTENSIONES_IMAGEN = {'.jpg', '.jpeg', '.png', '.webp'}


def _validar_tamano(archivo):
    if archivo.size > MAX_BYTES:
        raise serializers.ValidationError('El archivo supera el tamaño máximo permitido de 10 MB.')


def validar_documento(archivo):
    """Acepta PDF, DOC, DOCX y ODT; comprueba extensión, tamaño y firma real del archivo."""
    if archivo is None:
        return archivo
    _validar_tamano(archivo)
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in _FIRMAS_DOCUMENTO:
        raise serializers.ValidationError('Formato no permitido. Use PDF, DOC, DOCX u ODT.')
    cabecera = archivo.read(8)
    archivo.seek(0)
    if not any(cabecera.startswith(f) for f in _FIRMAS_DOCUMENTO[ext]):
        raise serializers.ValidationError('El contenido del archivo no coincide con su extensión.')
    return archivo


def validar_imagen(archivo):
    """Acepta JPG, PNG y WEBP de hasta 10 MB cuyo contenido sea realmente una imagen."""
    if archivo is None:
        return archivo
    _validar_tamano(archivo)
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in EXTENSIONES_IMAGEN:
        raise serializers.ValidationError('Formato de imagen no permitido. Use JPG, PNG o WEBP.')
    try:
        Image.open(archivo).verify()
    except Exception:
        raise serializers.ValidationError('El archivo no es una imagen válida.')
    finally:
        archivo.seek(0)
    return archivo
