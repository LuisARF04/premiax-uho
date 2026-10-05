import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';
import { Loading } from '../components/ui';

export default function ProponerGanadores() {
  const { id, premioId } = useParams();
  const navigate = useNavigate();
  const [propuestas, setPropuestas] = useState(null);
  const [selecciones, setSelecciones] = useState({});
  const [fundamentacion, setFundamentacion] = useState('');
  const [premio, setPremio] = useState(null);
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);

  function cargar() {
    api.get('/propuestas/', { params: { comision: id, premio: premioId, page_size: 200 } }).then((r) => {
      const items = r.data.results || r.data;
      setPropuestas(items);
      const sel = {};
      items.forEach((p) => { sel[p.id] = p.seleccion_comision || ''; });
      setSelecciones(sel);
    });
    api.get(`/premios/${premioId}/`).then((r) => setPremio(r.data));
  }
  useEffect(() => { cargar(); }, [id, premioId]);

  async function enviar() {
    setError('');
    const marcadas = Object.entries(selecciones).filter(([, v]) => v);
    if (!marcadas.length) {
      setError('Seleccione al menos un candidato como premio o reconocimiento.');
      return;
    }
    setEnviando(true);
    try {
      for (const [propuestaId, seleccion] of marcadas) {
        await api.post(`/propuestas/${propuestaId}/proponer_ganador/`, { seleccion_comision: seleccion, fundamentacion_comision: fundamentacion });
      }
      navigate(`/app/comisiones/${id}/panel`);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo enviar la propuesta de ganadores.');
    } finally {
      setEnviando(false);
    }
  }

  if (!propuestas || !premio) return <Loading />;

  return (
    <div>
      <div className="ph"><div><h2>Proponer Ganadores</h2><div className="phs">Premio: {premio.nombre} · Disponibles: {premio.cant_premios} premios, {premio.cant_reconocimientos} reconocimientos</div></div></div>
      <div className="ca" style={{ maxWidth: 780 }}>
        {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
        <div className="al-wn"><span>⚠️</span><div>Solo puedes proponer hasta <strong>{premio.cant_premios} premios</strong> y <strong>{premio.cant_reconocimientos} reconocimientos</strong>.</div></div>
        <div className="card mb16">
          <div className="ch"><h3>Propuestas Recibidas ({propuestas.length})</h3></div>
          <table className="dt">
            <thead><tr><th>Candidato</th><th>Área</th><th>Seleccionar como</th></tr></thead>
            <tbody>
              {propuestas.map((p) => (
                <tr key={p.id} style={selecciones[p.id] ? { background: '#EAFAF1' } : undefined}>
                  <td><strong>{p.candidato_nombre}</strong></td>
                  <td className="tsm">{p.area_nombre || '—'}</td>
                  <td>
                    <select className="fc" style={{ width: 175 }} value={selecciones[p.id] || ''}
                      onChange={(e) => setSelecciones({ ...selecciones, [p.id]: e.target.value })}>
                      <option value="">-- Sin selección --</option>
                      <option value="premio">🏆 Premio Rector</option>
                      <option value="reconocimiento">⭐ Reconocimiento</option>
                    </select>
                  </td>
                </tr>
              ))}
              {!propuestas.length && <tr><td colSpan={3} className="tm">No hay propuestas para este premio en tu comisión.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="card mb16">
          <div className="ch"><h3>✍️ Fundamentación de la Comisión</h3></div>
          <div className="cb">
            <textarea className="fc" rows={4} value={fundamentacion} onChange={(e) => setFundamentacion(e.target.value)}
              placeholder="Describa los criterios usados por la comisión para esta selección..." />
          </div>
        </div>
        <div className="flex g8">
          <button className="bs" onClick={() => navigate(-1)}>Volver</button>
          <button className="bp" style={{ flex: 1, justifyContent: 'center' }} disabled={enviando} onClick={enviar}>
            📤 Enviar propuesta de ganadores →
          </button>
        </div>
      </div>
    </div>
  );
}
