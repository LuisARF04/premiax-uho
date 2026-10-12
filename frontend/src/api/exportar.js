function descargar(blob, nombre) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nombre;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Exporta filas (arreglo de objetos) a CSV con BOM para que Excel respete los acentos.
export function exportarCSV(nombre, filas) {
  if (!filas?.length) return;
  const columnas = Object.keys(filas[0]);
  const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const lineas = [columnas.map(esc).join(','), ...filas.map((f) => columnas.map((c) => esc(f[c])).join(','))];
  descargar(new Blob(['\uFEFF' + lineas.join('\r\n')], { type: 'text/csv;charset=utf-8' }), `${nombre}.csv`);
}

// Exporta el primer <svg> de un contenedor (gráfico de Recharts) como imagen PNG.
export function exportarPNG(contenedor, nombre) {
  const svg = contenedor?.querySelector('svg.recharts-surface');
  if (!svg) return;
  const { width, height } = svg.getBoundingClientRect();
  const clon = svg.cloneNode(true);
  clon.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  clon.setAttribute('width', width);
  clon.setAttribute('height', height);
  const xml = new XMLSerializer().serializeToString(clon);
  const img = new Image();
  img.onload = () => {
    const escala = 2;
    const canvas = document.createElement('canvas');
    canvas.width = width * escala;
    canvas.height = height * escala;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.scale(escala, escala);
    ctx.drawImage(img, 0, 0, width, height);
    canvas.toBlob((blob) => blob && descargar(blob, `${nombre}.png`), 'image/png');
  };
  img.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(xml)}`;
}
