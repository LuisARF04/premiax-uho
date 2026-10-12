// Convierte la respuesta de error de la API ({detail} o errores por campo) en un texto legible.
export function mensajeError(err, porDefecto = 'Ocurrió un error. Intente de nuevo.') {
  const data = err?.response?.data;
  if (!data) return porDefecto;
  if (typeof data === 'string') return porDefecto;
  if (data.detail) return Array.isArray(data.detail) ? data.detail.join(' ') : String(data.detail);
  const partes = Object.entries(data).map(([campo, msgs]) => {
    const texto = Array.isArray(msgs) ? msgs.join(' ') : String(msgs);
    return campo === 'non_field_errors' ? texto : `${campo}: ${texto}`;
  });
  return partes.length ? partes.join(' ') : porDefecto;
}

export const MAX_ARCHIVO_MB = 10;
const EXTENSIONES_DOCUMENTO = ['.pdf', '.doc', '.docx', '.odt'];

// Validación previa en el navegador (el servidor valida de nuevo tipo real y tamaño, RNF-009).
export function validarDocumento(archivo) {
  if (!archivo) return '';
  if (archivo.size > MAX_ARCHIVO_MB * 1024 * 1024) return `El archivo supera el máximo de ${MAX_ARCHIVO_MB} MB.`;
  const nombre = archivo.name.toLowerCase();
  if (!EXTENSIONES_DOCUMENTO.some((ext) => nombre.endsWith(ext))) return 'Formato no permitido. Use PDF, DOC, DOCX u ODT.';
  return '';
}
