import { useEffect, useState } from 'react';
import api from '../api/client';
import { mensajeError } from '../api/errores';
import { PageHeader, Loading, Modal } from '../components/ui';

export default function Reglamento() {
  const [secciones, setSecciones] = useState(null);
  const [modal, setModal] = useState(null);
  const [error, setError] = useState('');

  function cargar() {
    api.get('/reglamento/').then((r) => setSecciones(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  async function guardar(form) {
    setError('');
    if (!form.titulo.trim() || !form.contenido.trim()) {
      setError('El título y el contenido son obligatorios.');
      return;
    }
    try {
      if (form.id) await api.patch(`/reglamento/${form.id}/`, form);
      else await api.post('/reglamento/', form);
      setModal(null);
      cargar();
    } catch (err) {
      setError(mensajeError(err, 'No se pudo guardar la sección.'));
    }
  }

  async function eliminar(s) {
    if (!confirm(`¿Eliminar la sección "${s.titulo}" del reglamento?`)) return;
    await api.delete(`/reglamento/${s.id}/`);
    cargar();
  }

  return (
    <div>
      <PageHeader title="Reglamento del Sistema" subtitle="Contenido que se muestra en el landing page; los cambios se publican de inmediato"
        actions={<button className="bp" onClick={() => { setError(''); setModal({}); }}>+ Nueva Sección</button>} />
      <div className="ca">
        {!secciones ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>#</th><th>Sección</th><th>Contenido</th><th>Visible</th><th>Acciones</th></tr></thead>
              <tbody>
                {secciones.map((s) => (
                  <tr key={s.id}>
                    <td>{s.orden}</td>
                    <td><strong>{s.icono} {s.titulo}</strong></td>
                    <td className="tsm tm" style={{ maxWidth: 420 }}>{s.contenido.length > 140 ? `${s.contenido.slice(0, 140)}…` : s.contenido}</td>
                    <td>{s.activo ? <span className="bg bg-gr">Publicada</span> : <span className="bg bg-gy">Oculta</span>}</td>
                    <td>
                      <button className="bs" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => { setError(''); setModal(s); }}>✏️</button>{' '}
                      <button className="bd" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => eliminar(s)}>🗑</button>
                    </td>
                  </tr>
                ))}
                {!secciones.length && <tr><td colSpan={5} className="tm">No hay secciones. Cree la primera para publicar el reglamento.</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {modal && <SeccionForm seccion={modal} error={error} onClose={() => setModal(null)} onSave={guardar} />}
    </div>
  );
}

function SeccionForm({ seccion, error, onClose, onSave }) {
  const [form, setForm] = useState({
    id: seccion.id, titulo: seccion.titulo || '', icono: seccion.icono ?? '📋', contenido: seccion.contenido || '',
    orden: seccion.orden ?? 1, activo: seccion.activo ?? true,
  });
  return (
    <Modal title={seccion.id ? 'Editar Sección' : 'Nueva Sección'} onClose={onClose} width={620}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg3 mb12">
        <div className="fg"><label>Icono</label><input className="fc" maxLength={10} value={form.icono} onChange={(e) => setForm({ ...form, icono: e.target.value })} /></div>
        <div className="fg"><label>Orden</label><input className="fc" type="number" min={0} value={form.orden} onChange={(e) => setForm({ ...form, orden: e.target.value })} /></div>
        <div className="fg"><label>Visible</label>
          <select className="fc" value={form.activo ? '1' : '0'} onChange={(e) => setForm({ ...form, activo: e.target.value === '1' })}>
            <option value="1">Publicada</option><option value="0">Oculta</option>
          </select>
        </div>
      </div>
      <div className="fg mb12"><label className="req">Título</label><input className="fc" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} /></div>
      <div className="fg mb16"><label className="req">Contenido</label>
        <textarea className="fc" rows={7} value={form.contenido} onChange={(e) => setForm({ ...form, contenido: e.target.value })} />
        <div className="tsm tm">Los saltos de línea se respetan en el landing page.</div>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
