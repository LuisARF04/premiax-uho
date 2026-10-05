import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { PageHeader, Loading, Modal, Avatar } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function Comisiones() {
  const { usuario, tienePrivilegio } = useAuth();
  const navigate = useNavigate();
  const [comisiones, setComisiones] = useState(null);
  const [premios, setPremios] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [modal, setModal] = useState(null);
  const [busquedaMiembro, setBusquedaMiembro] = useState({});
  const esGestor = tienePrivilegio('gestor_global');

  function cargar() {
    const endpoint = esGestor ? '/comisiones/' : '/comisiones-mias/';
    api.get(endpoint, { params: esGestor ? { page_size: 100 } : undefined }).then((r) => setComisiones(r.data.results || r.data));
  }
  useEffect(() => {
    cargar();
    if (esGestor) {
      api.get('/premios/', { params: { page_size: 200 } }).then((r) => setPremios(r.data.results || r.data));
      api.get('/usuarios/', { params: { mini: 1, page_size: 200 } }).then((r) => setUsuarios(r.data.results || r.data));
    }
  }, [esGestor]);

  async function guardarComision(form) {
    const payload = { ...form, jefe: form.jefe || null };
    if (form.id) await api.patch(`/comisiones/${form.id}/`, payload);
    else await api.post('/comisiones/', payload);
    setModal(null);
    cargar();
  }

  async function agregarMiembro(comisionId) {
    const usuarioId = busquedaMiembro[comisionId];
    if (!usuarioId) return;
    await api.post(`/comisiones/${comisionId}/agregar_miembro/`, { usuario: usuarioId });
    setBusquedaMiembro({ ...busquedaMiembro, [comisionId]: '' });
    cargar();
  }

  async function quitarMiembro(comisionId, miembroId) {
    await api.delete(`/comisiones/${comisionId}/miembros/${miembroId}/`);
    cargar();
  }

  return (
    <div>
      <PageHeader
        title={esGestor ? 'Gestión de Comisiones' : 'Mis Comisiones'}
        subtitle={comisiones ? `${comisiones.length} comisiones` : ''}
        actions={esGestor && <button className="bp" onClick={() => setModal({})}>+ Nueva Comisión</button>}
      />
      <div className="ca">
        {!comisiones ? <Loading /> : (
          <div className="g2">
            {comisiones.map((c) => (
              <div className="card" key={c.id}>
                <div className="ch" style={{ background: 'var(--light)' }}>
                  <div><h3>{c.nombre}</h3><div className="tsm tm">Dirige: {c.jefe_detalle?.nombre_completo || '—'}</div></div>
                  <span className="bg bg-bl" style={{ marginLeft: 'auto' }}>{c.propuestas_revisadas_count}/{c.propuestas_count} revisadas</span>
                </div>
                <div className="cb">
                  <div style={{ fontSize: '.77rem', color: 'var(--muted)', marginBottom: 7, fontWeight: 600 }}>MIEMBROS ({c.miembros.length})</div>
                  <div className="flex g8 mb12" style={{ flexWrap: 'wrap' }}>
                    {c.miembros.map((m) => (
                      <div key={m.id} className="flex ic g8" style={{ background: 'var(--pale)', padding: '4px 8px', borderRadius: 20 }}>
                        <Avatar nombre={m.usuario_detalle.nombre_completo} size={22} />
                        <span className="tsm">{m.usuario_detalle.nombre_completo}</span>
                        {esGestor && <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--danger)' }} onClick={() => quitarMiembro(c.id, m.id)}>✕</button>}
                      </div>
                    ))}
                    {!c.miembros.length && <span className="tm tsm">Sin miembros asignados.</span>}
                  </div>
                  {esGestor && (
                    <div className="flex g8 mb12">
                      <select className="fc" value={busquedaMiembro[c.id] || ''} onChange={(e) => setBusquedaMiembro({ ...busquedaMiembro, [c.id]: e.target.value })}>
                        <option value="">Añadir miembro...</option>
                        {usuarios.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo}</option>)}
                      </select>
                      <button className="bs" onClick={() => agregarMiembro(c.id)}>Añadir</button>
                    </div>
                  )}
                  <div style={{ fontSize: '.77rem', color: 'var(--muted)', marginBottom: 5, fontWeight: 600 }}>PREMIOS ASIGNADOS ({c.premios_detalle.length})</div>
                  <div style={{ fontSize: '.8rem', lineHeight: 1.7, color: 'var(--muted)' }}>{c.premios_detalle.map((p) => p.nombre).join(' · ') || 'Ninguno'}</div>
                  <div className="flex g8 mt12">
                    <button className="bs" style={{ flex: 1, fontSize: '.78rem' }} onClick={() => navigate(`/app/comisiones/${c.id}/panel`)}>Ver Panel</button>
                    {esGestor && <button className="bs" style={{ fontSize: '.78rem' }} onClick={() => setModal(c)}>✏️</button>}
                  </div>
                </div>
              </div>
            ))}
            {!comisiones.length && <div className="empty-state">No hay comisiones para mostrar.</div>}
          </div>
        )}
      </div>
      {modal && <ComisionForm comision={modal} premios={premios} usuarios={usuarios} onClose={() => setModal(null)} onSave={guardarComision} />}
    </div>
  );
}

function ComisionForm({ comision, premios, usuarios, onClose, onSave }) {
  const [form, setForm] = useState({
    id: comision.id, nombre: comision.nombre || '', jefe: comision.jefe || '',
    premios: comision.premios_detalle ? comision.premios_detalle.map((p) => p.id) : [],
  });
  function togglePremio(id) {
    setForm((f) => ({ ...f, premios: f.premios.includes(id) ? f.premios.filter((x) => x !== id) : [...f.premios, id] }));
  }
  return (
    <Modal title={comision.id ? 'Editar Comisión' : 'Nueva Comisión'} onClose={onClose} width={560}>
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb12">
        <label className="req">Jefe de Comisión</label>
        <select className="fc" value={form.jefe} onChange={(e) => setForm({ ...form, jefe: e.target.value })}>
          <option value="">Seleccionar...</option>
          {usuarios.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo}</option>)}
        </select>
      </div>
      <div className="fg mb16">
        <label>Premios asignados</label>
        <div style={{ maxHeight: 200, overflowY: 'auto', border: '1px solid var(--border)', borderRadius: 7, padding: 8 }}>
          {premios.map((p) => (
            <label key={p.id} style={{ display: 'flex', gap: 7, alignItems: 'center', fontSize: '.83rem', padding: '3px 0' }}>
              <input type="checkbox" checked={form.premios.includes(p.id)} onChange={() => togglePremio(p.id)} /> {p.nombre}
            </label>
          ))}
        </div>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
