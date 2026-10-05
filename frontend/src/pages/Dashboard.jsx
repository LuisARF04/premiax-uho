import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { PageHeader, Loading, EstadoBadge, KpiCard } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { usuario, tienePrivilegio } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get('/dashboard/principal/').then((r) => setData(r.data));
  }, []);

  if (!data) return <Loading />;

  return (
    <div>
      <PageHeader
        title="Dashboard Principal"
        subtitle={`Bienvenido/a, ${usuario?.nombre_completo} · ${data.etapa_activa ? `Etapa activa: ${data.etapa_activa}` : 'Sin etapa activa'}`}
        actions={<>
          <button className="bs" onClick={() => navigate('/app/propuestas/nueva')}>+ Nueva Propuesta</button>
          {tienePrivilegio('gestor_global') && <button className="bp" onClick={() => navigate('/app/estadisticas')}>📈 Estadísticas</button>}
        </>}
      />
      <div className="ca">
        {data.dias_restantes != null && (
          <div className="al-wn"><span>⚠️</span><div><strong>Etapa activa:</strong> {data.etapa_activa}. Quedan <strong>{data.dias_restantes} días</strong>.</div></div>
        )}
        <div className="kg">
          <KpiCard icon="📝" value={data.kpis.propuestas_recibidas} label="Propuestas Recibidas" color="bl" />
          <KpiCard icon="🏛️" value={data.kpis.comisiones_activas} label="Comisiones Activas" color="go" />
          <KpiCard icon="✅" value={data.kpis.propuestas_evaluadas} label="Propuestas Evaluadas" color="gr" />
          <KpiCard icon="⏰" value={data.kpis.dias_restantes ?? '—'} label="Días Restantes" color="re" />
        </div>
        <div className="g2">
          <div className="card">
            <div className="ch"><h3>Últimas Propuestas</h3>
              <button className="bs" style={{ marginLeft: 'auto', fontSize: '.76rem', padding: '4px 10px' }} onClick={() => navigate('/app/propuestas')}>Ver todas →</button>
            </div>
            <table className="dt">
              <thead><tr><th>Candidato</th><th>Premio</th><th>Estado</th></tr></thead>
              <tbody>
                {data.ultimas_propuestas.map((p) => (
                  <tr key={p.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/propuestas/${p.id}`)}>
                    <td><div className="tb">{p.candidato_nombre}</div><div className="tsm tm">{p.area_nombre || '—'}</div></td>
                    <td style={{ fontSize: '.79rem' }}>{p.premio_nombre}</td>
                    <td><EstadoBadge estado={p.estado} /></td>
                  </tr>
                ))}
                {!data.ultimas_propuestas.length && <tr><td colSpan={3} className="tm">Sin propuestas todavía.</td></tr>}
              </tbody>
            </table>
          </div>
          <div className="card">
            <div className="ch"><h3>Estado de Comisiones</h3>
              {tienePrivilegio('gestor_global') && <button className="bs" style={{ marginLeft: 'auto', fontSize: '.76rem', padding: '4px 10px' }} onClick={() => navigate('/app/comisiones')}>Gestionar →</button>}
            </div>
            <div className="cb">
              {data.comisiones_progreso.map((c) => (
                <div className="mb16" key={c.id}>
                  <div className="flex ic g8 mb12" style={{ fontSize: '.83rem', justifyContent: 'space-between' }}>
                    <span className="tb">{c.nombre}</span><span className="tm">{c.revisadas}/{c.total}</span>
                  </div>
                  <div className="prg"><div className="prb" style={{ width: `${c.porcentaje}%` }} /></div>
                </div>
              ))}
              {!data.comisiones_progreso.length && <div className="tm">Sin comisiones activas.</div>}
            </div>
          </div>
        </div>
        <div className="card mt16">
          <div className="ch"><h3>📅 Próximas Fechas del Proceso</h3></div>
          <table className="dt">
            <thead><tr><th>Etapa</th><th>Fecha Límite</th><th>Responsable</th><th>Estado</th></tr></thead>
            <tbody>
              {data.proximas_etapas.map((e) => (
                <tr key={e.id}>
                  <td>{e.nombre}</td><td><strong>{e.fecha_cierre}</strong></td><td>{e.responsable}</td>
                  <td><EstadoBadge estado={e.estado} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
