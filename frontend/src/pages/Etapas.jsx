import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading, Modal, EstadoBadge } from '../components/ui';

export default function Etapas() {
  const [etapas, setEtapas] = useState(null);
  const [modal, setModal] = useState(null);
  const [error, setError] = useState('');

  function cargar() {
    api.get('/etapas/', { params: { page_size: 100, ordering: 'orden' } }).then((r) => setEtapas(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  async function guardar(form) {
    setError('');
    try {
      if (form.id) await api.patch(`/etapas/${form.id}/`, form);
      else await api.post('/etapas/', form);
      setModal(null); cargar();
    } catch { setError('No se pudo guardar la etapa. Verifique las fechas.'); }
  }

  async function eliminar(e) {
    if (!confirm(`¿Eliminar la etapa "${e.nombre}"?`)) return;
    await api.delete(`/etapas/${e.id}/`);
    cargar();
  }

  return (
    <div>
      <PageHeader title="Etapas del Proceso" subtitle={etapas ? `Proceso ${etapas[0]?.anio ?? ''} — ${etapas.length} etapas configuradas` : ''}
        actions={<button className="bp" onClick={() => setModal({})}>+ Nueva Etapa</button>} />
      <div className="ca">
        {!etapas ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>#</th><th>Etapa</th><th>Fecha Inicio</th><th>Fecha Cierre</th><th>Responsable</th><th>Estado</th><th>Acción</th></tr></thead>
              <tbody>
                {etapas.map((e) => (
                  <tr key={e.id} style={e.estado === 'en_curso' ? { background: '#FEF9E7' } : undefined}>
                    <td>{e.orden}</td>
                    <td><strong>{e.nombre}</strong>{e.descripcion && <div className="tsm tm">{e.descripcion}</div>}</td>
                    <td>{e.fecha_inicio}</td><td>{e.fecha_cierre}</td><td>{e.responsable_desc}</td>
                    <td><EstadoBadge estado={e.estado} /></td>
                    <td><button className="bs" style={{ fontSize: '.73rem', padding: '3px 7px' }} onClick={() => setModal(e)}>✏️</button>{' '}
                      <button className="bd" style={{ fontSize: '.73rem', padding: '3px 7px' }} onClick={() => eliminar(e)}>🗑</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {modal && <EtapaForm etapa={modal} error={error} onClose={() => setModal(null)} onSave={guardar} />}
    </div>
  );
}

function EtapaForm({ etapa, error, onClose, onSave }) {
  const [form, setForm] = useState({
    id: etapa.id, nombre: etapa.nombre || '', descripcion: etapa.descripcion || '',
    fecha_inicio: etapa.fecha_inicio || '', fecha_cierre: etapa.fecha_cierre || '',
    anio: etapa.anio || new Date().getFullYear(), orden: etapa.orden ?? 1, responsable_desc: etapa.responsable_desc || '',
  });
  return (
    <Modal title={etapa.id ? 'Editar Etapa' : 'Nueva Etapa'} onClose={onClose}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb12"><label>Descripción</label><textarea className="fc" rows={2} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></div>
      <div className="fg2 mb12">
        <div className="fg"><label className="req">Fecha Inicio</label><input className="fc" type="date" value={form.fecha_inicio} onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })} /></div>
        <div className="fg"><label className="req">Fecha Cierre</label><input className="fc" type="date" value={form.fecha_cierre} onChange={(e) => setForm({ ...form, fecha_cierre: e.target.value })} /></div>
      </div>
      <div className="fg3 mb16">
        <div className="fg"><label>Año</label><input className="fc" type="number" value={form.anio} onChange={(e) => setForm({ ...form, anio: e.target.value })} /></div>
        <div className="fg"><label>Orden</label><input className="fc" type="number" value={form.orden} onChange={(e) => setForm({ ...form, orden: e.target.value })} /></div>
        <div className="fg"><label>Responsable</label><input className="fc" value={form.responsable_desc} onChange={(e) => setForm({ ...form, responsable_desc: e.target.value })} /></div>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
