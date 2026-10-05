import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Modal } from '../components/ui';

const CATALOGOS = [
  { key: 'categorias-docentes', titulo: '🎓 Cat. Docentes' },
  { key: 'categorias-cientificas', titulo: '🔬 Cat. Científicas' },
  { key: 'cargos', titulo: '👔 Cargos' },
  { key: 'carreras', titulo: '🎯 Carreras' },
];

function Catalogo({ endpoint, titulo }) {
  const [items, setItems] = useState(null);
  const [modal, setModal] = useState(null);
  const [nombre, setNombre] = useState('');

  function cargar() {
    api.get(`/${endpoint}/`, { params: { page_size: 100 } }).then((r) => setItems(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, []);

  function abrirModal(item) {
    setModal(item || {});
    setNombre(item?.nombre || '');
  }

  async function guardar() {
    if (!nombre.trim()) return;
    if (modal.id) await api.patch(`/${endpoint}/${modal.id}/`, { nombre });
    else await api.post(`/${endpoint}/`, { nombre });
    setModal(null);
    cargar();
  }

  async function eliminar(item) {
    if (!confirm(`¿Eliminar "${item.nombre}"?`)) return;
    await api.delete(`/${endpoint}/${item.id}/`);
    cargar();
  }

  return (
    <div className="card">
      <div className="ch"><h3>{titulo}</h3><button className="bp" style={{ marginLeft: 'auto', fontSize: '.73rem', padding: '4px 9px' }} onClick={() => abrirModal(null)}>+</button></div>
      <div className="cb">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
          {(items || []).map((it) => (
            <div key={it.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 10px', background: 'var(--pale)', borderRadius: 6, fontSize: '.83rem' }}>
              <span>{it.nombre}</span>
              <div style={{ display: 'flex', gap: 3 }}>
                <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => abrirModal(it)}>✏️</button>
                <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => eliminar(it)}>🗑</button>
              </div>
            </div>
          ))}
          {items && !items.length && <div className="tm tsm">Sin elementos.</div>}
        </div>
      </div>
      {modal && (
        <Modal title={modal.id ? `Editar` : `Nuevo elemento`} onClose={() => setModal(null)} width={380}>
          <div className="fg mb16"><label className="req">Nombre</label><input className="fc" value={nombre} onChange={(e) => setNombre(e.target.value)} autoFocus /></div>
          <button className="bp wf jc" onClick={guardar}>Guardar</button>
        </Modal>
      )}
    </div>
  );
}

export default function Nomencladores() {
  return (
    <div>
      <PageHeader title="Nomencladores" subtitle="Gestión de catálogos del sistema" />
      <div className="ca">
        <div className="g3">
          {CATALOGOS.map((c) => <Catalogo key={c.key} endpoint={c.key} titulo={c.titulo} />)}
        </div>
      </div>
    </div>
  );
}
