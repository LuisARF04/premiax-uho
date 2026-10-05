import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { PageHeader, Loading, EstadoBadge } from '../components/ui';
import { useAuth } from '../context/AuthContext';

const TABS = [
  { key: '', label: 'Todas' },
  { key: 'pendiente_departamento', label: 'Pendientes Dpto.' },
  { key: 'pendiente_area', label: 'Pendientes Área' },
  { key: 'en_comision', label: 'En Comisión' },
  { key: 'aprobada', label: 'Aprobadas' },
];

export default function Propuestas() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [propuestas, setPropuestas] = useState(null);
  const [tab, setTab] = useState('');
  const [busqueda, setBusqueda] = useState('');

  function cargar() {
    api.get('/propuestas/', { params: { estado: tab || undefined, search: busqueda || undefined, page_size: 100 } })
      .then((r) => setPropuestas(r.data.results || r.data));
  }
  useEffect(() => { cargar(); }, [tab, busqueda]);

  return (
    <div>
      <PageHeader
        title="Propuestas de Premios"
        subtitle={usuario?.area_nombre ? `${usuario.area_nombre} — propuestas visibles según tu rol` : 'Propuestas visibles según tu rol'}
        actions={<>
          <input className="fc" style={{ width: 190 }} placeholder="🔍 Buscar candidato..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          <button className="bp" onClick={() => navigate('/app/propuestas/nueva')}>+ Nueva</button>
        </>}
      />
      <div className="ca">
        <div className="tabs">
          {TABS.map((t) => <div key={t.key} className={`tab ${tab === t.key ? 'on' : ''}`} onClick={() => setTab(t.key)}>{t.label}</div>)}
        </div>
        {!propuestas ? <Loading /> : (
          <div className="card">
            <table className="dt">
              <thead><tr><th>Candidato</th><th>Premio</th><th>Nivel</th><th>Estado</th><th>Fecha</th><th>Acción</th></tr></thead>
              <tbody>
                {propuestas.map((p) => (
                  <tr key={p.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/propuestas/${p.id}`)}>
                    <td><div className="tb">{p.candidato_nombre}</div><div className="tsm tm">{p.departamento_nombre || p.area_nombre || '—'}</div></td>
                    <td className="tsm">{p.premio_nombre}</td>
                    <td><span className="bg bg-bl">{p.nivel_actual}</span></td>
                    <td><EstadoBadge estado={p.estado} /></td>
                    <td className="tsm tm">{new Date(p.fecha_creacion).toLocaleDateString()}</td>
                    <td><button className="bs" style={{ fontSize: '.73rem', padding: '3px 8px' }} onClick={(e) => { e.stopPropagation(); navigate(`/app/propuestas/${p.id}`); }}>Ver →</button></td>
                  </tr>
                ))}
                {!propuestas.length && <tr><td colSpan={6} className="tm">No hay propuestas para este filtro.</td></tr>}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
