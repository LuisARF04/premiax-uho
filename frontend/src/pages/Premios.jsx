import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading, Modal } from '../components/ui';

const TIPOS = [
  ['ind_docente', 'Individuales Docentes'], ['ind_no_docente', 'Individuales No Docentes'],
  ['col_docente', 'Colectivos Docentes'], ['col_no_docente', 'Colectivos No Docentes'],
];
const COLOR_TIPO = { ind_docente: 'bg-bl', ind_no_docente: 'bg-go', col_docente: 'bg-go', col_no_docente: 'bg-re' };

export default function Premios() {
  const [categorias, setCategorias] = useState(null);
  const [modalCat, setModalCat] = useState(null);
  const [modalPremio, setModalPremio] = useState(null);
  const [error, setError] = useState('');

  function cargar() {
    api.get('/categorias-premio/', { params: { page_size: 100 } }).then((r) => setCategorias(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  async function guardarCategoria(form) {
    setError('');
    try {
      if (form.id) await api.patch(`/categorias-premio/${form.id}/`, form);
      else await api.post('/categorias-premio/', form);
      setModalCat(null); cargar();
    } catch { setError('No se pudo guardar la categoría.'); }
  }

  async function guardarPremio(form) {
    setError('');
    try {
      if (form.id) await api.patch(`/premios/${form.id}/`, form);
      else await api.post('/premios/', form);
      setModalPremio(null); cargar();
    } catch { setError('No se pudo guardar el premio.'); }
  }

  async function eliminarPremio(p) {
    if (!confirm(`¿Eliminar el premio "${p.nombre}"?`)) return;
    await api.delete(`/premios/${p.id}/`);
    cargar();
  }

  return (
    <div>
      <PageHeader title="Categorías y Premios" subtitle="Define los premios y sus criterios de evaluación"
        actions={<button className="bp" onClick={() => setModalCat({})}>+ Nueva Categoría</button>} />
      <div className="ca">
        {!categorias ? <Loading /> : categorias.map((cat) => (
          <div className="card mb16" key={cat.id}>
            <div className="ch" style={{ background: 'var(--light)' }}>
              <h3>{cat.nombre}</h3>
              <span className={`bg ${COLOR_TIPO[cat.tipo]}`} style={{ marginLeft: 7 }}>{cat.premios.length} premios</span>
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 7 }}>
                <button className="bs" style={{ fontSize: '.76rem', padding: '4px 10px' }} onClick={() => setModalPremio({ categoria: cat.id })}>+ Premio</button>
                <button className="bs" style={{ fontSize: '.76rem', padding: '4px 10px' }} onClick={() => setModalCat(cat)}>✏️</button>
              </div>
            </div>
            <table className="dt">
              <thead><tr><th>Premio</th><th>Premios</th><th>Reconoc.</th><th>Por Comisión</th><th>Acciones</th></tr></thead>
              <tbody>
                {cat.premios.map((p) => (
                  <tr key={p.id}>
                    <td><strong>{p.nombre}</strong><div className="tsm tm">{p.criterios}</div></td>
                    <td>{p.cant_premios}</td>
                    <td>{p.cant_reconocimientos}</td>
                    <td>{p.es_por_comision ? <span className="bg bg-gr">Sí</span> : 'No'}</td>
                    <td>
                      <button className="bs" style={{ fontSize: '.73rem', padding: '3px 7px' }} onClick={() => setModalPremio(p)}>✏️</button>{' '}
                      <button className="bd" style={{ fontSize: '.73rem', padding: '3px 7px' }} onClick={() => eliminarPremio(p)}>🗑</button>
                    </td>
                  </tr>
                ))}
                {!cat.premios.length && <tr><td colSpan={5} className="tm">Sin premios definidos.</td></tr>}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      {modalCat && <CategoriaForm categoria={modalCat} error={error} onClose={() => setModalCat(null)} onSave={guardarCategoria} />}
      {modalPremio && <PremioForm premio={modalPremio} categorias={categorias} error={error} onClose={() => setModalPremio(null)} onSave={guardarPremio} />}
    </div>
  );
}

function CategoriaForm({ categoria, error, onClose, onSave }) {
  const [form, setForm] = useState({ id: categoria.id, nombre: categoria.nombre || '', tipo: categoria.tipo || TIPOS[0][0], descripcion: categoria.descripcion || '' });
  return (
    <Modal title={categoria.id ? 'Editar Categoría' : 'Nueva Categoría'} onClose={onClose}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb16">
        <label className="req">Tipo</label>
        <select className="fc" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
          {TIPOS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}

function PremioForm({ premio, categorias, error, onClose, onSave }) {
  const [form, setForm] = useState({
    id: premio.id, nombre: premio.nombre || '', criterios: premio.criterios || '',
    categoria: premio.categoria || categorias[0]?.id, cant_premios: premio.cant_premios ?? 1,
    cant_reconocimientos: premio.cant_reconocimientos ?? 0, es_por_comision: premio.es_por_comision ?? false,
  });
  return (
    <Modal title={premio.id ? 'Editar Premio' : 'Nuevo Premio'} onClose={onClose}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Nombre</label><input className="fc" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></div>
      <div className="fg mb12"><label>Criterios</label><textarea className="fc" rows={3} value={form.criterios} onChange={(e) => setForm({ ...form, criterios: e.target.value })} /></div>
      <div className="fg mb12">
        <label className="req">Categoría</label>
        <select className="fc" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })}>
          {categorias.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
        </select>
      </div>
      <div className="fg3 mb12">
        <div className="fg"><label>Cant. Premios</label><input className="fc" type="number" min={0} value={form.cant_premios} onChange={(e) => setForm({ ...form, cant_premios: e.target.value })} /></div>
        <div className="fg"><label>Cant. Reconoc.</label><input className="fc" type="number" min={0} value={form.cant_reconocimientos} onChange={(e) => setForm({ ...form, cant_reconocimientos: e.target.value })} /></div>
        <div className="fg"><label>Por comisión</label>
          <select className="fc" value={form.es_por_comision ? '1' : '0'} onChange={(e) => setForm({ ...form, es_por_comision: e.target.value === '1' })}>
            <option value="0">No</option><option value="1">Sí</option>
          </select>
        </div>
      </div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
