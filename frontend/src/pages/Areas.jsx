import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading, Modal } from '../components/ui';

export default function Areas() {
  const [tab, setTab] = useState('areas');
  const [areas, setAreas] = useState(null);
  const [usuarios, setUsuarios] = useState([]);
  const [modalArea, setModalArea] = useState(null);
  const [modalDepto, setModalDepto] = useState(null);
  const [error, setError] = useState('');

  function cargar() {
    api.get('/areas/', { params: { page_size: 100 } }).then((r) => setAreas(r.data.results || r.data));
  }
  useEffect(() => {
    cargar();
    api.get('/usuarios/', { params: { mini: 1, page_size: 200 } }).then((r) => setUsuarios(r.data.results || r.data));
  }, []);

  const departamentos = (areas || []).flatMap((a) => a.departamentos.map((d) => ({ ...d, area_nombre: a.nombre })));

  async function guardarArea(form) {
    setError('');
    const payload = { ...form, responsable: form.responsable || null };
    try {
      if (form.id) await api.patch(`/areas/${form.id}/`, payload);
      else await api.post('/areas/', payload);
      setModalArea(null);
      cargar();
    } catch (err) { setError('No se pudo guardar el área.'); }
  }

  async function eliminarArea(a) {
    if (!confirm(`¿Eliminar el área "${a.nombre}"? Esta acción no se puede deshacer.`)) return;
    await api.delete(`/areas/${a.id}/`);
    cargar();
  }

  async function guardarDepto(form) {
    setError('');
    const payload = { ...form, responsable: form.responsable || null };
    try {
      if (form.id) await api.patch(`/departamentos/${form.id}/`, payload);
      else await api.post('/departamentos/', payload);
      setModalDepto(null);
      cargar();
    } catch (err) { setError('No se pudo guardar el departamento.'); }
  }

  async function eliminarDepto(d) {
    if (!confirm(`¿Eliminar el departamento "${d.nombre}"?`)) return;
    await api.delete(`/departamentos/${d.id}/`);
    cargar();
  }

  async function importarCsv(e) {
    const archivo = e.target.files[0];
    if (!archivo) return;
    const fd = new FormData();
    fd.append('archivo', archivo);
    try {
      const { data } = await api.post('/areas/importar_excel/', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      alert(`Importadas ${data.areas_creadas} áreas y ${data.departamentos_creados} departamentos.`);
      cargar();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al importar el archivo.');
    }
    e.target.value = '';
  }

  return (
    <div>
      <PageHeader
        title="Áreas y Departamentos"
        subtitle="Gestión del organigrama universitario"
        actions={<>
          <label className="bs" style={{ cursor: 'pointer' }}>
            📥 Importar CSV
            <input type="file" accept=".csv" hidden onChange={importarCsv} />
          </label>
          <button className="bp" onClick={() => (tab === 'areas' ? setModalArea({}) : setModalDepto({}))}>+ Nueva {tab === 'areas' ? 'Área' : 'Departamento'}</button>
        </>}
      />
      <div className="ca">
        <div className="tabs">
          <div className={`tab ${tab === 'areas' ? 'on' : ''}`} onClick={() => setTab('areas')}>Áreas ({areas?.length ?? '…'})</div>
          <div className={`tab ${tab === 'deptos' ? 'on' : ''}`} onClick={() => setTab('deptos')}>Departamentos ({departamentos.length})</div>
        </div>
        {!areas ? <Loading /> : tab === 'areas' ? (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Nombre del Área</th><th>Responsable</th><th>Departamentos</th><th>Propuestas</th><th>Acciones</th></tr></thead>
              <tbody>
                {areas.map((a) => (
                  <tr key={a.id}>
                    <td><strong>{a.nombre}</strong></td>
                    <td>{a.responsable_nombre || '—'}</td>
                    <td>{a.departamentos_count}</td>
                    <td><span className="bg bg-bl">{a.propuestas_count}</span></td>
                    <td>
                      <button className="bs" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => setModalArea(a)}>✏️</button>{' '}
                      <button className="bd" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => eliminarArea(a)}>🗑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Nombre</th><th>Área</th><th>Responsable</th><th>Propuestas</th><th>Acciones</th></tr></thead>
              <tbody>
                {departamentos.map((d) => (
                  <tr key={d.id}>
                    <td><strong>{d.nombre}</strong></td>
                    <td>{d.area_nombre}</td>
                    <td>{d.responsable_nombre || '—'}</td>
                    <td><span className="bg bg-bl">{d.propuestas_count}</span></td>
                    <td>
                      <button className="bs" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => setModalDepto(d)}>✏️</button>{' '}
                      <button className="bd" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => eliminarDepto(d)}>🗑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modalArea && (
        <AreaForm area={modalArea} usuarios={usuarios} error={error} onClose={() => setModalArea(null)} onSave={guardarArea} />
      )}
      {modalDepto && (
        <DeptoForm depto={modalDepto} areas={areas} usuarios={usuarios} error={error} onClose={() => setModalDepto(null)} onSave={guardarDepto} />
      )}
    </div>
  );
}

function AreaForm({ area, usuarios, error, onClose, onSave }) {
  const [form, setForm] = useState({ id: area.id, nombre: area.nombre || '', descripcion: area.descripcion || '', responsable: area.responsable || '' });
  return (
    <Modal title={area.id ? 'Editar Área' : 'Nueva Área'} onClose={onClose}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb12"><label>Descripción</label><textarea className="fc" rows={2} value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} /></div>
      <div className="fg mb16">
        <label>Responsable</label>
        <select className="fc" value={form.responsable} onChange={(e) => setForm({ ...form, responsable: e.target.value })}>
          <option value="">Sin asignar</option>
          {usuarios.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo}</option>)}
        </select>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}

function DeptoForm({ depto, areas, usuarios, error, onClose, onSave }) {
  const [form, setForm] = useState({ id: depto.id, nombre: depto.nombre || '', area: depto.area || (areas[0]?.id ?? ''), responsable: depto.responsable || '' });
  return (
    <Modal title={depto.id ? 'Editar Departamento' : 'Nuevo Departamento'} onClose={onClose}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb12">
        <label className="req">Área</label>
        <select className="fc" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })}>
          {areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
        </select>
      </div>
      <div className="fg mb16">
        <label>Responsable</label>
        <select className="fc" value={form.responsable} onChange={(e) => setForm({ ...form, responsable: e.target.value })}>
          <option value="">Sin asignar</option>
          {usuarios.map((u) => <option key={u.id} value={u.id}>{u.nombre_completo}</option>)}
        </select>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
