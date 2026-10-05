import { useEffect, useState } from 'react';
import api from '../api/client';
import { PageHeader, Loading } from '../components/ui';

export default function Estadisticas() {
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [data, setData] = useState(null);
  const [inactivos, setInactivos] = useState(null);

  useEffect(() => {
    api.get('/dashboard/estadisticas/', { params: { anio } }).then((r) => setData(r.data));
  }, [anio]);
  useEffect(() => {
    api.get('/usuarios-inactivos/').then((r) => setInactivos(r.data)).catch(() => setInactivos([]));
  }, []);

  if (!data) return <Loading />;

  const maxArea = Math.max(1, ...data.propuestas_por_area.map((a) => a.total));

  return (
    <div>
      <PageHeader title="Dashboard Estadístico" subtitle="Proceso de Premiación"
        actions={<select className="fc" style={{ width: 130 }} value={anio} onChange={(e) => setAnio(e.target.value)}>
          {[anio, anio - 1, anio - 2].map((a) => <option key={a} value={a}>Año {a}</option>)}
        </select>} />
      <div className="ca">
        <div className="kg kg5">
          <div className="kc bl"><div className="ki">📝</div><div className="kv">{data.total_propuestas}</div><div className="kl">Total propuestas</div></div>
          <div className="kc go"><div className="ki">🏆</div><div className="kv">{data.total_ganadores_propuestos}</div><div className="kl">Ganadores propuestos</div></div>
          <div className="kc gr"><div className="ki">✅</div><div className="kv">{data.total_aprobados}</div><div className="kl">Aprobados</div></div>
          <div className="kc bl"><div className="ki">🏢</div><div className="kv">{data.areas_participantes}</div><div className="kl">Áreas participantes</div></div>
          <div className="kc re"><div className="ki">⏰</div><div className="kv">{data.areas_sin_propuesta}</div><div className="kl">Áreas sin prop.</div></div>
        </div>
        <div className="g2">
          <div className="card">
            <div className="ch"><h3>Propuestas por Área</h3></div>
            <div className="cb">
              <div className="bc2">
                {data.propuestas_por_area.map((a) => (
                  <div className="br" key={a.area__nombre}>
                    <div className="brl">{a.area__nombre}</div>
                    <div className="brt"><div className="brf" style={{ width: `${(a.total / maxArea) * 100}%` }}>{a.total}</div></div>
                  </div>
                ))}
                {!data.propuestas_por_area.length && <div className="tm">Sin datos.</div>}
              </div>
            </div>
          </div>
          <div className="card">
            <div className="ch"><h3>Propuestas por Categoría</h3></div>
            <div className="cb">
              <div className="bc2">
                {data.propuestas_por_categoria.map((c) => (
                  <div className="br" key={c.premio__categoria__nombre}>
                    <div className="brl">{c.premio__categoria__nombre}</div>
                    <div className="brt"><div className="brf" style={{ width: `${(c.total / (data.total_propuestas || 1)) * 100}%` }}>{c.total}</div></div>
                  </div>
                ))}
                {!data.propuestas_por_categoria.length && <div className="tm">Sin datos.</div>}
              </div>
            </div>
          </div>
        </div>
        <div className="card mt16">
          <div className="ch"><h3>⚠️ Usuarios Inactivos — No han revisado propuestas</h3></div>
          <table className="dt">
            <thead><tr><th>Usuario</th><th>Rol</th><th>Área</th><th>Días inactivo</th><th>Pendientes</th></tr></thead>
            <tbody>
              {(inactivos || []).map((u) => (
                <tr key={u.id}><td><strong>{u.nombre}</strong></td><td><span className="bg bg-go">{u.rol}</span></td><td>{u.area || '—'}</td>
                  <td className="tsm tm">{u.dias_inactivo != null ? `Hace ${u.dias_inactivo} días` : 'Nunca ha entrado'}</td><td>{u.pendientes}</td></tr>
              ))}
              {inactivos && !inactivos.length && <tr><td colSpan={5} className="tm">Todos los usuarios responsables están activos.</td></tr>}
              {!inactivos && <tr><td colSpan={5}><Loading /></td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
