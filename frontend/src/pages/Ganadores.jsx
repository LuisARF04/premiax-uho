import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading, Modal } from '../components/ui';

export default function Ganadores() {
  const [ganadores, setGanadores] = useState(null);
  const [premios, setPremios] = useState([]);
  const [anio, setAnio] = useState('');
  const [modal, setModal] = useState(null);
  const [error, setError] = useState('');

  function cargar() {
    api.get('/ganadores/', { params: { anio: anio || undefined, page_size: 200, ordering: '-anio' } }).then((r) => setGanadores(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, [anio]);
  useEffect(() => { api.get('/premios/', { params: { page_size: 200 } }).then((r) => setPremios(r.data.results || r.data)); }, []);

  async function guardar(form) {
    setError('');
    try {
      await api.post('/ganadores/', form);
      setModal(null);
      cargar();
    } catch { setError('No se pudo registrar el ganador.'); }
  }

  async function eliminar(g) {
    if (!confirm(`¿Eliminar el registro de "${g.persona_nombre}"?`)) return;
    await api.delete(`/ganadores/${g.id}/`);
    cargar();
  }

  return (
    <div>
      <PageHeader title="Ganadores / Registro Retroactivo" subtitle="Historial de premiados y carga retroactiva de años anteriores (RF-023)"
        actions={<>
          <input className="fc" style={{ width: 110 }} type="number" placeholder="Año" value={anio} onChange={(e) => setAnio(e.target.value)} />
          <button className="bp" onClick={() => setModal({})}>+ Registrar Ganador</button>
        </>} />
      <div className="ca">
        {!ganadores ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Persona / Colectivo</th><th>Premio</th><th>Tipo</th><th>Año</th><th>Publicado</th><th>Acciones</th></tr></thead>
              <tbody>
                {ganadores.map((g) => (
                  <tr key={g.id}>
                    <td><strong>{g.persona_nombre}</strong><div className="tsm tm">{g.persona_area}</div></td>
                    <td className="tsm">{g.premio_nombre}</td>
                    <td><span className={`bg ${g.tipo === 'premio' ? 'bg-go' : 'bg-bl'}`}>{g.tipo}</span></td>
                    <td>{g.anio}</td>
                    <td>{g.publicado ? <span className="bg bg-gr">Sí</span> : <span className="bg bg-gy">No</span>}</td>
                    <td><button className="bd" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={() => eliminar(g)}>🗑</button></td>
                  </tr>
                ))}
                {!ganadores.length && <tr><td colSpan={6} className="tm">No hay ganadores registrados para este filtro.</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {modal && <GanadorForm premios={premios} error={error} onClose={() => setModal(null)} onSave={guardar} />}
    </div>
  );
}

function GanadorForm({ premios, error, onClose, onSave }) {
  const [form, setForm] = useState({
    premio: premios[0]?.id || '', persona_nombre: '', persona_area: '', categoria_docente: '', categoria_cientifica: '',
    tipo: 'premio', anio: new Date().getFullYear() - 1, fundamentacion: '',
  });
  return (
    <Modal title="Registrar Ganador Retroactivo" onClose={onClose} width={560}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg2 mb12">
        <div className="fg"><label className="req">Persona / Colectivo</label><input className="fc" value={form.persona_nombre} onChange={(e) => setForm({ ...form, persona_nombre: e.target.value })} /></div>
        <div className="fg"><label>Área</label><input className="fc" value={form.persona_area} onChange={(e) => setForm({ ...form, persona_area: e.target.value })} /></div>
      </div>
      <div className="fg mb12">
        <label className="req">Premio</label>
        <select className="fc" value={form.premio} onChange={(e) => setForm({ ...form, premio: e.target.value })}>
          {premios.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
        </select>
      </div>
      <div className="fg3 mb12">
        <div className="fg"><label>Cat. Docente</label><input className="fc" value={form.categoria_docente} onChange={(e) => setForm({ ...form, categoria_docente: e.target.value })} /></div>
        <div className="fg"><label>Cat. Científica</label><input className="fc" value={form.categoria_cientifica} onChange={(e) => setForm({ ...form, categoria_cientifica: e.target.value })} /></div>
        <div className="fg"><label>Año</label><input className="fc" type="number" value={form.anio} onChange={(e) => setForm({ ...form, anio: e.target.value })} /></div>
      </div>
      <div className="fg mb12">
        <label>Tipo</label>
        <select className="fc" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
          <option value="premio">Premio</option><option value="reconocimiento">Reconocimiento</option>
        </select>
      </div>
      <div className="fg mb16"><label>Fundamentación</label><textarea className="fc" rows={3} value={form.fundamentacion} onChange={(e) => setForm({ ...form, fundamentacion: e.target.value })} /></div>
      <button className="bp wf jc" onClick={() => onSave(form)}>Guardar</button>
    </Modal>
  );
}
