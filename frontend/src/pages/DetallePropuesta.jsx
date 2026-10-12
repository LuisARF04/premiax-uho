import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';
import { Loading, EstadoBadge, Avatar, Modal } from '../components/ui';
import { mensajeError, validarDocumento } from '../api/errores';
import { useAuth } from '../context/AuthContext';

export default function DetallePropuesta() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { usuario, tienePrivilegio } = useAuth();
  const [propuesta, setPropuesta] = useState(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const [motivo, setMotivo] = useState('');
  const [comision, setComision] = useState(null);
  const [editando, setEditando] = useState(false);

  function cargar() {
    api.get(`/propuestas/${id}/`).then((r) => setPropuesta(r.data)).catch(() => setError('No tienes acceso a esta propuesta o no existe.'));
  }
  useEffect(() => { cargar(); }, [id]);
  useEffect(() => {
    if (propuesta?.comision) api.get(`/comisiones/${propuesta.comision}/`).then((r) => setComision(r.data)).catch(() => setComision(null));
    else setComision(null);
  }, [propuesta?.comision]);

  async function accion(nombre, payload) {
    setCargando(true);
    setError('');
    try {
      await api.post(`/propuestas/${id}/${nombre}/`, payload || {});
      cargar();
    } catch (err) {
      setError(mensajeError(err, 'No se pudo completar la acción.'));
    } finally {
      setCargando(false);
    }
  }

  if (error && !propuesta) return <div className="ca"><div className="al-re"><span>⚠️</span><div>{error}</div></div></div>;
  if (!propuesta) return <Loading />;

  const puedeElevarDepto = propuesta.nivel_actual === 'departamento' && (usuario.rol === 'jefe_departamento' || tienePrivilegio('gestor_global'));
  const puedeElevarArea = propuesta.nivel_actual === 'area' && (usuario.rol === 'jefe_area' || tienePrivilegio('gestor_global'));
  const esJefeDeSuComision = propuesta.comision && propuesta.comision_nombre;
  // RF-019/020: quién puede modificar o enriquecer la propuesta (espeja la regla del servidor).
  const puedeEditar = !['aprobada', 'rechazada'].includes(propuesta.estado) && (
    tienePrivilegio('gestor_global')
    || (propuesta.nivel_actual === 'departamento' && (propuesta.creado_por === usuario.id
      || (usuario.rol === 'jefe_departamento' && propuesta.departamento === usuario.departamento)))
    || (propuesta.nivel_actual === 'area' && usuario.rol === 'jefe_area' && propuesta.area === usuario.area)
  );
  const esJefeDeComision = !!propuesta.comision && (tienePrivilegio('gestor_global') || comision?.jefe === usuario.id);
  const miRevision = propuesta.revisiones.find((r) => r.miembro === usuario.id);
  const mostrarRevisiones = propuesta.revisiones.length > 0 || (esJefeDeComision && propuesta.estado === 'en_comision');
  const puedeAprobar = propuesta.estado === 'ganadora_propuesta' && tienePrivilegio('gestor_global');

  return (
    <div>
      <div className="ph">
        <div>
          <div className="bc"><button onClick={() => navigate('/app/propuestas')}>Propuestas</button><span className="sep">›</span><span>Detalle #{propuesta.id}</span></div>
          <h2>Propuesta: {propuesta.premio_detalle?.nombre} <span className="bg bg-gy" style={{ verticalAlign: 'middle' }}>v{propuesta.version}</span></h2>
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

            {mostrarRevisiones && (
              <RevisionesComision
                propuesta={propuesta} comision={comision} esJefe={esJefeDeComision} miRevision={miRevision}
                accion={accion} cargando={cargando}
              />
            )}

            <div className="card mb16">
              <div className="ch"><h3>🗂️ Versiones</h3></div>
              <div className="cb">
                {propuesta.versiones.map((v) => (
                  <div className="hl" key={v.id}>
                    <div className="ht">{new Date(v.fecha).toLocaleString()}</div>
                    <div className="ha2">
                      <strong>Versión {v.version}{v.version === propuesta.version ? ' (actual)' : ''}</strong> — {v.usuario_nombre} · {v.candidato_nombre}
                      {v.documento && <> · <a href={v.documento} target="_blank" rel="noreferrer">📎 documento</a></>}
                    </div>
                  </div>
                ))}
                {!propuesta.versiones.length && <div className="tm tsm">Esta propuesta se registró antes del control de versiones.</div>}
              </div>
            </div>

            <div className="card">
              <div className="ch"><h3>⚙️ Acciones</h3></div>
              <div className="cb">
                <div className="flex g8" style={{ flexWrap: 'wrap' }}>
                  {puedeEditar && <button className="bs" disabled={cargando} onClick={() => setEditando(true)}>✏️ Modificar / Enriquecer</button>}
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
      {editando && <EditarPropuesta propuesta={propuesta} onClose={() => setEditando(false)} onGuardado={() => { setEditando(false); cargar(); }} />}
    </div>
  );
}

function EditarPropuesta({ propuesta, onClose, onGuardado }) {
  const [candidato, setCandidato] = useState(propuesta.candidato_nombre);
  const [resumen, setResumen] = useState(propuesta.resumen);
  const [documento, setDocumento] = useState(null);
  const [error, setError] = useState('');
  const [guardando, setGuardando] = useState(false);

  async function guardar() {
    const problema = validarDocumento(documento);
    if (problema) return setError(problema);
    if (!candidato.trim() || !resumen.trim()) return setError('El candidato y la descripción son obligatorios.');
    setGuardando(true);
    try {
      const fd = new FormData();
      fd.append('candidato_nombre', candidato);
      fd.append('resumen', resumen);
      if (documento) fd.append('documento', documento);
      await api.patch(`/propuestas/${propuesta.id}/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      onGuardado();
    } catch (err) {
      setError(mensajeError(err, 'No se pudo guardar la propuesta.'));
      setGuardando(false);
    }
  }

  return (
    <Modal title={`Modificar propuesta (versión ${propuesta.version} → ${propuesta.version + 1})`} onClose={onClose} width={620}>
      {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
      <div className="fg mb12"><label className="req">Candidato</label><input className="fc" value={candidato} onChange={(e) => setCandidato(e.target.value)} /></div>
      <div className="fg mb12"><label className="req">Descripción / fundamentación</label><textarea className="fc" rows={5} value={resumen} onChange={(e) => setResumen(e.target.value)} /></div>
      <div className="fg mb16">
        <label>Reemplazar documento (opcional)</label>
        {propuesta.documento && <div className="tsm tm mb12">Actual: <a href={propuesta.documento} target="_blank" rel="noreferrer">descargar documento</a>. Al subir uno nuevo, el anterior queda en el historial de versiones.</div>}
        <input className="fc" type="file" accept=".pdf,.doc,.docx,.odt" onChange={(e) => { setError(validarDocumento(e.target.files[0])); setDocumento(e.target.files[0] || null); }} />
        <div className="tsm tm">PDF, DOC, DOCX u ODT — máx. 10 MB</div>
      </div>
      <button className="bp wf jc" disabled={guardando} onClick={guardar}>{guardando ? 'Guardando…' : 'Guardar cambios'}</button>
    </Modal>
  );
}

function RevisionesComision({ propuesta, comision, esJefe, miRevision, accion, cargando }) {
  const [miembro, setMiembro] = useState('');
  const [criterio, setCriterio] = useState(miRevision?.criterio || '');
  const [puntuacion, setPuntuacion] = useState(miRevision?.puntuacion ?? '');

  const asignados = new Set(propuesta.revisiones.map((r) => r.miembro));
  const disponibles = (comision?.miembros || []).filter((m) => !asignados.has(m.usuario));

  return (
    <div className="card mb16">
      <div className="ch"><h3>🧑‍⚖️ Revisiones de la Comisión</h3></div>
      <div className="cb">
        {esJefe && propuesta.estado === 'en_comision' && (
          <div className="flex g8 mb12" style={{ flexWrap: 'wrap' }}>
            <select className="fc" style={{ flex: 1, minWidth: 180 }} value={miembro} onChange={(e) => setMiembro(e.target.value)}>
              <option value="">Asignar revisión a un miembro…</option>
              {disponibles.map((m) => <option key={m.usuario} value={m.usuario}>{m.usuario_detalle?.nombre_completo}</option>)}
            </select>
            <button className="bp" disabled={!miembro || cargando} onClick={() => { accion('asignar_revision', { miembro }); setMiembro(''); }}>Asignar</button>
          </div>
        )}
        {esJefe && comision && !comision.miembros.length && <div className="tm tsm mb12">La comisión no tiene miembros. Añádelos desde «Comisiones».</div>}
        {propuesta.revisiones.map((r) => (
          <div className="hl" key={r.id}>
            <div className="ht">{r.revisada ? `Revisada ${new Date(r.fecha_revision).toLocaleString()}` : `Asignada ${new Date(r.fecha_asignacion).toLocaleString()}`}</div>
            <div className="ha2">
              <strong>{r.miembro_nombre}</strong> {r.revisada ? <span className="bg bg-gr">Revisada{r.puntuacion != null ? ` · ${r.puntuacion}/10` : ''}</span> : <span className="bg bg-wn">Pendiente</span>}
              {r.criterio && <div className="tsm" style={{ marginTop: 4, whiteSpace: 'pre-line' }}>{r.criterio}</div>}
              {esJefe && propuesta.estado === 'en_comision' && (
                <button className="bd" style={{ fontSize: '.7rem', padding: '2px 7px', marginTop: 4 }} disabled={cargando}
                  onClick={() => accion('quitar_revision', { revision: r.id })}>Quitar asignación</button>
              )}
            </div>
          </div>
        ))}
        {!propuesta.revisiones.length && <div className="tm tsm">Aún no hay revisiones asignadas.</div>}

        {miRevision && (
          <div className="mt12" style={{ borderTop: '1px solid var(--border)', paddingTop: 12 }}>
            <div style={{ fontWeight: 700, fontSize: '.83rem', color: 'var(--blue)', marginBottom: 6 }}>Tu revisión</div>
            <div className="fg mb12"><label className="req">Criterio</label>
              <textarea className="fc" rows={3} value={criterio} onChange={(e) => setCriterio(e.target.value)} placeholder="Valoración de los méritos del candidato…" /></div>
            <div className="fg mb12" style={{ maxWidth: 160 }}><label>Puntuación (1-10)</label>
              <input className="fc" type="number" min={1} max={10} value={puntuacion} onChange={(e) => setPuntuacion(e.target.value)} /></div>
            <button className="bp" disabled={cargando || !criterio.trim()} onClick={() => accion('registrar_revision', { criterio, puntuacion })}>
              {miRevision.revisada ? 'Actualizar revisión' : 'Enviar revisión'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
