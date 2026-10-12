import { useEffect, useRef, useState } from 'react';
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import api from '../api/client';
import { exportarCSV, exportarPNG } from '../api/exportar';
import { useAuth } from '../context/AuthContext';
import { PageHeader, Loading } from '../components/ui';

const COLORES = ['#003366', '#C9A227', '#1A7F4B', '#C0392B', '#5B8DB8', '#8E6C1F', '#4E8F6B', '#9B59B6'];
const REFRESCO_MS = 30000; // «tiempo real»: el dashboard se vuelve a consultar cada 30 s.

function ChartCard({ titulo, filas, nombreArchivo, children, alto = 260 }) {
  const ref = useRef(null);
  return (
    <div className="card">
      <div className="ch">
        <h3>{titulo}</h3>
        <div className="flex g8">
          <button className="bs" style={{ fontSize: '.7rem', padding: '3px 8px' }} disabled={!filas?.length} onClick={() => exportarCSV(nombreArchivo, filas)}>⬇ CSV</button>
          <button className="bs" style={{ fontSize: '.7rem', padding: '3px 8px' }} disabled={!filas?.length} onClick={() => exportarPNG(ref.current, nombreArchivo)}>🖼 PNG</button>
        </div>
      </div>
      <div className="cb" ref={ref}>
        {filas?.length ? <div style={{ width: '100%', height: alto }}><ResponsiveContainer>{children}</ResponsiveContainer></div> : <div className="tm">Sin datos para este año.</div>}
      </div>
    </div>
  );
}

function BarrasHorizontales({ datos, clave, etiqueta, ancho = 150 }) {
  return (
    <BarChart data={datos} layout="vertical" margin={{ left: 8, right: 16 }}>
      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
      <XAxis type="number" allowDecimals={false} />
      <YAxis type="category" dataKey={etiqueta} width={ancho} tick={{ fontSize: 11 }} />
      <Tooltip />
      <Bar dataKey={clave} name="Propuestas" fill="#003366" radius={[0, 4, 4, 0]} />
    </BarChart>
  );
}

export default function Estadisticas() {
  const { tienePrivilegio } = useAuth();
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [data, setData] = useState(null);
  const [inactivos, setInactivos] = useState(null);

  useEffect(() => {
    let activo = true;
    const cargar = () => api.get('/dashboard/estadisticas/', { params: { anio } }).then((r) => activo && setData(r.data));
    cargar();
    const t = setInterval(cargar, REFRESCO_MS);
    return () => { activo = false; clearInterval(t); };
  }, [anio]);

  useEffect(() => {
    if (!tienePrivilegio('gestor_global')) { setInactivos(false); return undefined; }
    const cargar = () => api.get('/usuarios-inactivos/').then((r) => setInactivos(r.data)).catch(() => setInactivos(false));
    cargar();
    const t = setInterval(cargar, REFRESCO_MS);
    return () => clearInterval(t);
  }, []);

  if (!data) return <Loading />;

  const porArea = data.propuestas_por_area.map((a) => ({ nombre: a.area__nombre, total: a.total }));
  const porPremio = data.propuestas_por_premio.map((p) => ({ nombre: p.premio__nombre, categoria: p.premio__categoria__nombre, total: p.total }));
  const porDepto = data.propuestas_por_departamento.map((d) => ({ nombre: d.departamento__nombre, area: d.departamento__area__nombre, total: d.total }));
  const porCategoria = data.propuestas_por_categoria.map((c) => ({ nombre: c.premio__categoria__nombre, total: c.total }));
  const participacion = data.participacion_roles.map((r) => ({ Rol: r.rol, Usuarios: r.total, 'Con propuestas': r.con_propuestas, 'Activos 7 días': r.activos_7_dias }));

  // Ganadores por categoría y año: una fila por año con una columna por categoría.
  const categoriasGanadores = [...new Set(data.ganadores_por_anio.map((g) => g.premio__categoria__nombre))];
  const ganadoresAnio = Object.values(data.ganadores_por_anio.reduce((acc, g) => {
    acc[g.anio] = acc[g.anio] || { anio: String(g.anio) };
    acc[g.anio][g.premio__categoria__nombre] = g.total;
    return acc;
  }, {}));
  const ganadoresCsv = data.ganadores_por_anio.map((g) => ({ Año: g.anio, Categoría: g.premio__categoria__nombre, Ganadores: g.total }));

  const enviaron = data.estado_por_area.filter((a) => a.envio).length;
  const estadoAreaPie = [{ nombre: 'Enviaron propuestas', valor: enviaron }, { nombre: 'No enviaron', valor: data.estado_por_area.length - enviaron }];

  return (
    <div>
      <PageHeader title="Dashboard Estadístico" subtitle={`Proceso de Premiación · actualizado ${new Date(data.actualizado).toLocaleTimeString()} (se refresca cada 30 s)`}
        actions={<select className="fc" style={{ width: 130 }} value={anio} onChange={(e) => setAnio(Number(e.target.value))}>
          {[0, 1, 2].map((d) => new Date().getFullYear() - d).map((a) => <option key={a} value={a}>Año {a}</option>)}
        </select>} />
      <div className="ca">
        <div className="kg kg5">
          <div className="kc bl"><div className="ki">📝</div><div className="kv">{data.total_propuestas}</div><div className="kl">Total propuestas</div></div>
          <div className="kc go"><div className="ki">🏆</div><div className="kv">{data.total_ganadores_propuestos}</div><div className="kl">Ganadores propuestos</div></div>
          <div className="kc gr"><div className="ki">✅</div><div className="kv">{data.total_aprobados}</div><div className="kl">Aprobados</div></div>
          <div className="kc bl"><div className="ki">🏢</div><div className="kv">{data.areas_participantes}</div><div className="kl">Áreas participantes</div></div>
          <div className="kc re"><div className="ki">⏰</div><div className="kv">{data.areas_sin_propuesta}</div><div className="kl">Áreas sin prop.</div></div>
        </div>

        <div className="g2 mb16">
          <ChartCard titulo="Propuestas por tipo de premio" nombreArchivo={`propuestas-por-premio-${anio}`}
            filas={porPremio.map((p) => ({ Premio: p.nombre, Categoría: p.categoria, Propuestas: p.total }))} alto={Math.max(240, porPremio.length * 32)}>
            <BarrasHorizontales datos={porPremio} clave="total" etiqueta="nombre" ancho={170} />
          </ChartCard>
          <ChartCard titulo="Propuestas por categoría" nombreArchivo={`propuestas-por-categoria-${anio}`}
            filas={porCategoria.map((c) => ({ Categoría: c.nombre, Propuestas: c.total }))}>
            <PieChart>
              <Pie data={porCategoria} dataKey="total" nameKey="nombre" outerRadius={90} label={({ value }) => value}>
                {porCategoria.map((_, i) => <Cell key={i} fill={COLORES[i % COLORES.length]} />)}
              </Pie>
              <Tooltip /><Legend />
            </PieChart>
          </ChartCard>
        </div>

        <div className="g2 mb16">
          <ChartCard titulo="Áreas con más propuestas enviadas" nombreArchivo={`propuestas-por-area-${anio}`}
            filas={porArea.map((a) => ({ Área: a.nombre, Propuestas: a.total }))} alto={Math.max(240, porArea.length * 32)}>
            <BarrasHorizontales datos={porArea} clave="total" etiqueta="nombre" ancho={170} />
          </ChartCard>
          <ChartCard titulo="Departamentos con más propuestas (top 10)" nombreArchivo={`propuestas-por-departamento-${anio}`}
            filas={porDepto.map((d) => ({ Departamento: d.nombre, Área: d.area, Propuestas: d.total }))} alto={Math.max(240, porDepto.length * 32)}>
            <BarrasHorizontales datos={porDepto} clave="total" etiqueta="nombre" ancho={170} />
          </ChartCard>
        </div>

        <div className="g2 mb16">
          <ChartCard titulo="Estado del proceso por área" nombreArchivo={`estado-por-area-${anio}`}
            filas={data.estado_por_area.map((a) => ({ Área: a.area, 'Envió propuestas': a.envio ? 'Sí' : 'No', Propuestas: a.propuestas }))}>
            <PieChart>
              <Pie data={estadoAreaPie} dataKey="valor" nameKey="nombre" outerRadius={90} label={({ value }) => value}>
                <Cell fill="#1A7F4B" /><Cell fill="#C0392B" />
              </Pie>
              <Tooltip /><Legend />
            </PieChart>
          </ChartCard>
          <ChartCard titulo="Ganadores por categoría y año" nombreArchivo="ganadores-por-categoria-y-anio" filas={ganadoresCsv}>
            <BarChart data={ganadoresAnio}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="anio" /><YAxis allowDecimals={false} /><Tooltip /><Legend />
              {categoriasGanadores.map((c, i) => <Bar key={c} dataKey={c} stackId="a" fill={COLORES[i % COLORES.length]} />)}
            </BarChart>
          </ChartCard>
        </div>

        <div className="mb16">
          <ChartCard titulo="Participación de usuarios y roles" nombreArchivo={`participacion-roles-${anio}`} filas={participacion}>
            <BarChart data={participacion}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="Rol" tick={{ fontSize: 11 }} /><YAxis allowDecimals={false} /><Tooltip /><Legend />
              <Bar dataKey="Usuarios" fill="#003366" /><Bar dataKey="Con propuestas" fill="#C9A227" /><Bar dataKey="Activos 7 días" fill="#1A7F4B" />
            </BarChart>
          </ChartCard>
        </div>

        {inactivos !== false && (
          <div className="card mt16">
            <div className="ch">
              <h3>⚠️ Control de usuarios inactivos</h3>
              {inactivos && (
                <button className="bs" style={{ fontSize: '.7rem', padding: '3px 8px' }}
                  onClick={() => exportarCSV('usuarios-inactivos', inactivos.usuarios.map((u) => ({
                    Usuario: u.nombre, Rol: u.rol, Área: u.area || '', 'Días sin ingresar': u.dias_inactivo ?? 'Nunca ingresó', 'Propuestas sin revisar': u.pendientes,
                  })))}>⬇ CSV</button>
              )}
            </div>
            {!inactivos ? <div className="cb"><Loading /></div> : (
              <>
                <div className="cb tsm tm">
                  Sin ingresar en los últimos {inactivos.periodo.dias} días o con propuestas pendientes de revisión en {inactivos.periodo.anio}
                  {inactivos.periodo.etapa_activa ? ` · etapa activa: ${inactivos.periodo.etapa_activa}` : ''}.
                </div>
                <table className="dt">
                  <thead><tr><th>Rol</th><th>Usuarios</th><th>Sin ingresar</th><th>Propuestas sin revisar</th></tr></thead>
                  <tbody>
                    {inactivos.por_rol.map((r) => (
                      <tr key={r.rol}><td><strong>{r.rol_nombre}</strong></td><td>{r.total}</td>
                        <td>{r.sin_ingreso ? <span className="bg bg-wn">{r.sin_ingreso}</span> : 0}</td><td>{r.propuestas_sin_revisar}</td></tr>
                    ))}
                  </tbody>
                </table>
                <table className="dt mt16">
                  <thead><tr><th>Usuario</th><th>Rol</th><th>Área</th><th>Último ingreso</th><th>Sin revisar</th></tr></thead>
                  <tbody>
                    {inactivos.usuarios.map((u) => (
                      <tr key={u.id}><td><strong>{u.nombre}</strong></td><td><span className="bg bg-go">{u.rol}</span></td><td>{u.area || '—'}</td>
                        <td className="tsm tm">{u.dias_inactivo != null ? `Hace ${u.dias_inactivo} días` : 'Nunca ha entrado'}</td>
                        <td>{u.pendientes ? <span className="bg bg-re">{u.pendientes}</span> : 0}</td></tr>
                    ))}
                    {!inactivos.usuarios.length && <tr><td colSpan={5} className="tm">Todos los usuarios responsables están al día.</td></tr>}
                  </tbody>
                </table>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
