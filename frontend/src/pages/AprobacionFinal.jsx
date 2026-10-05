import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { PageHeader, Loading } from '../components/ui';

export default function AprobacionFinal() {
  const navigate = useNavigate();
  const [propuestas, setPropuestas] = useState(null);
  const [seleccionadas, setSeleccionadas] = useState(new Set());
  const [procesando, setProcesando] = useState(false);

  function cargar() {
    api.get('/propuestas/', { params: { estado: 'ganadora_propuesta', page_size: 200 } }).then((r) => setPropuestas(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  function toggle(id) {
    setSeleccionadas((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  async function aprobar(id) {
    setProcesando(true);
    await api.post(`/propuestas/${id}/aprobar/`);
    setProcesando(false);
    cargar();
  }

  async function rechazar(id) {
    const motivo = prompt('Motivo del rechazo (opcional):') || '';
    setProcesando(true);
    await api.post(`/propuestas/${id}/rechazar/`, { motivo });
    setProcesando(false);
    cargar();
  }

  async function aprobarSeleccionadas() {
    setProcesando(true);
    for (const id of seleccionadas) {
      await api.post(`/propuestas/${id}/aprobar/`);
    }
    setProcesando(false);
    setSeleccionadas(new Set());
    cargar();
  }

  if (!propuestas) return <Loading />;

  return (
    <div>
      <PageHeader title="Aprobación Final de Ganadores" subtitle="Revisar y aprobar los ganadores propuestos por las comisiones"
        actions={<button className="bsuc" disabled={!seleccionadas.size || procesando} onClick={aprobarSeleccionadas}>✅ Aprobar seleccionados ({seleccionadas.size})</button>} />
      <div className="ca">
        <div className="al-info"><span>ℹ️</span><div>Las comisiones han propuesto ganadores. Los aprobados se publicarán automáticamente en el Landing Page.</div></div>
        <div className="card">
          <table className="dt">
            <thead><tr><th><input type="checkbox" disabled /></th><th>Candidato</th><th>Premio</th><th>Tipo</th><th>Comisión</th><th>Detalle</th><th>Decisión</th></tr></thead>
            <tbody>
              {propuestas.map((p) => (
                <tr key={p.id}>
                  <td><input type="checkbox" checked={seleccionadas.has(p.id)} onChange={() => toggle(p.id)} /></td>
                  <td><strong>{p.candidato_nombre}</strong><div className="tsm tm">{p.area_nombre}</div></td>
                  <td className="tsm">{p.premio_nombre}</td>
                  <td><span className={`bg ${p.seleccion_comision === 'premio' ? 'bg-go' : 'bg-bl'}`}>{p.seleccion_comision === 'premio' ? 'Premio' : 'Reconocimiento'}</span></td>
                  <td className="tsm">{p.comision_nombre}</td>
                  <td><button className="bs" style={{ fontSize: '.73rem', padding: '3px 9px' }} onClick={() => navigate(`/app/propuestas/${p.id}`)}>📄 Ver</button></td>
                  <td>
                    <div className="flex g8">
                      <button className="bsuc" style={{ fontSize: '.76rem', padding: '4px 11px' }} disabled={procesando} onClick={() => aprobar(p.id)}>✅</button>
                      <button className="bd" style={{ fontSize: '.76rem', padding: '4px 9px' }} disabled={procesando} onClick={() => rechazar(p.id)}>✗</button>
                    </div>
                  </td>
                </tr>
              ))}
              {!propuestas.length && <tr><td colSpan={7} className="tm">No hay ganadores propuestos pendientes de aprobación.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
