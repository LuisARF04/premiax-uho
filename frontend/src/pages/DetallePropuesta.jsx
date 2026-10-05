import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';
import { Loading, EstadoBadge, Avatar } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function DetallePropuesta() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { usuario, tienePrivilegio } = useAuth();
  const [propuesta, setPropuesta] = useState(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const [motivo, setMotivo] = useState('');

  function cargar() {
    api.get(`/propuestas/${id}/`).then((r) => setPropuesta(r.data)).catch(() => setError('No tienes acceso a esta propuesta o no existe.'));
  }
  useEffect(() => { cargar(); }, [id]);

  async function accion(nombre, payload) {
    setCargando(true);
    setError('');
    try {
      await api.post(`/propuestas/${id}/${nombre}/`, payload || {});
      cargar();
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo completar la acción.');
    } finally {
      setCargando(false);
    }
  }

  if (error && !propuesta) return <div className="ca"><div className="al-re"><span>⚠️</span><div>{error}</div></div></div>;
  if (!propuesta) return <Loading />;

  const puedeElevarDepto = propuesta.nivel_actual === 'departamento' && (usuario.rol === 'jefe_departamento' || tienePrivilegio('gestor_global'));
  const puedeElevarArea = propuesta.nivel_actual === 'area' && (usuario.rol === 'jefe_area' || tienePrivilegio('gestor_global'));
  const esJefeDeSuComision = propuesta.comision && propuesta.comision_nombre;
  const puedeAprobar = propuesta.estado === 'ganadora_propuesta' && tienePrivilegio('gestor_global');

  return (
    <div>
      <div className="ph">
        <div>
          <div className="bc"><button onClick={() => navigate('/app/propuestas')}>Propuestas</button><span className="sep">›</span><span>Detalle #{propuesta.id}</span></div>
          <h2>Propuesta: {propuesta.premio_detalle?.nombre}</h2>
          <div className="phs">{propuesta.candidato_nombre} · {propuesta.area_nombre || 'Sin área'}</div>
        </div>
        <div className="ha"><EstadoBadge estado={propuesta.estado} /></div>
      </div>
      <div className="ca">
        {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
        <div className="g2">
          <div>
            <div className="card mb16">
              <div className="ch"><h3>👤 Candidato</h3></div>
              <div className="cb">
                <div className="flex ic g12 mb16">
                  <Avatar nombre={propuesta.candidato_nombre} size={60} />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '1rem' }}>{propuesta.candidato_nombre}</div>
                    <div className="tsm tm">{propuesta.candidato_usuario_detalle?.rol || 'Candidato / Colectivo'}</div>
                    <div className="tsm" style={{ color: 'var(--blue)', marginTop: 3 }}>{propuesta.area_nombre} {propuesta.departamento_nombre ? `· ${propuesta.departamento_nombre}` : ''}</div>
                  </div>
                </div>
                <div className="hr" />
                <div className="fg2" style={{ gap: 10 }}>
                  <div><div style={{ fontSize: '.7rem', color: 'var(--muted)', fontWeight: 600 }}>PREMIO</div><div style={{ fontSize: '.86rem', fontWeight: 500, marginTop: 2 }}>{propuesta.premio_detalle?.nombre}</div></div>
                  <div><div style={{ fontSize: '.7rem', color: 'var(--muted)', fontWeight: 600 }}>AÑO</div><div style={{ fontSize: '.86rem', fontWeight: 500, marginTop: 2 }}>{propuesta.anio}</div></div>
                  <div><div style={{ fontSize: '.7rem', color: 'var(--muted)', fontWeight: 600 }}>NIVEL ACTUAL</div><div style={{ fontSize: '.86rem', fontWeight: 500, marginTop: 2 }}>{propuesta.nivel_actual}</div></div>
                  <div><div style={{ fontSize: '.7rem', color: 'var(--muted)', fontWeight: 600 }}>COMISIÓN</div><div style={{ fontSize: '.86rem', fontWeight: 500, marginTop: 2 }}>{propuesta.comision_nombre || '—'}</div></div>
                </div>
              </div>
            </div>
            <div className="card mb16">
              <div className="ch"><h3>📄 Resumen</h3></div>
              <div className="cb">
                <p style={{ fontSize: '.86rem', lineHeight: 1.75 }}>{propuesta.resumen}</p>
                {propuesta.documento && (
                  <div className="mt12" style={{ padding: 11, background: 'var(--pale)', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 9 }}>
                    <span style={{ fontSize: '1.4rem' }}>📎</span>
                    <div>Documento de fundamentación</div>
                    <a className="bs" style={{ marginLeft: 'auto', fontSize: '.78rem', padding: '4px 11px' }} href={propuesta.documento} target="_blank" rel="noreferrer">📥 Descargar</a>
                  </div>
                )}
                {propuesta.fundamentacion_comision && (
                  <div className="mt12">
                    <div style={{ fontWeight: 700, fontSize: '.83rem', color: 'var(--blue)', marginBottom: 4 }}>Fundamentación de la comisión:</div>
                    <p style={{ fontSize: '.84rem', color: 'var(--muted)' }}>{propuesta.fundamentacion_comision}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="card">
              <div className="ch"><h3>⚙️ Acciones</h3></div>
              <div className="cb">
                <div className="flex g8" style={{ flexWrap: 'wrap' }}>
                  {puedeElevarDepto && <button className="bp" disabled={cargando} onClick={() => accion('elevar')}>↑ Elevar a Área</button>}
                  {puedeElevarArea && <button className="bp" disabled={cargando} onClick={() => accion('elevar')}>↑ Elevar a Comisión / Universidad</button>}
                  {esJefeDeSuComision && propuesta.estado === 'en_comision' && (usuario.rol === 'jefe_comision' || tienePrivilegio('gestor_global')) && (
                    <button className="bp" disabled={cargando} onClick={() => navigate(`/app/comisiones/${propuesta.comision}/proponer-ganadores/${propuesta.premio}`)}>🏆 Proponer como Ganador</button>
                  )}
                  {puedeAprobar && (
                    <>
                      <button className="bsuc" disabled={cargando} onClick={() => accion('aprobar')}>✅ Aprobar Definitivamente</button>
                      <button className="bd" disabled={cargando} onClick={() => { const m = prompt('Motivo del rechazo (opcional):') || ''; setMotivo(m); accion('rechazar', { motivo: m }); }}>✗ Rechazar</button>
                    </>
                  )}
                  {tienePrivilegio('gestor_global') && propuesta.nivel_actual === 'comision' && (
                    <button className="bs" disabled={cargando} onClick={() => navigate('/app/comisiones')}>🔁 Reasignar Comisión</button>
                  )}
                  {!puedeElevarDepto && !puedeElevarArea && !puedeAprobar && (
                    <div className="tm tsm">No hay acciones disponibles para tu rol en el estado actual de esta propuesta.</div>
                  )}
                </div>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="ch"><h3>📜 Historial</h3></div>
            <div className="cb">
              {propuesta.historial.map((h) => (
                <div className="hl" key={h.id}>
                  <div className="ht">{new Date(h.fecha).toLocaleString()}</div>
                  <div className="ha2"><strong>{h.usuario_nombre}</strong> {h.usuario_rol ? `(${h.usuario_rol})` : ''} — {h.accion}. {h.descripcion}</div>
                </div>
              ))}
              {!propuesta.historial.length && <div className="tm">Sin historial registrado.</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
