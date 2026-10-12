import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { mensajeError, validarDocumento } from '../api/errores';
import { useAuth } from '../context/AuthContext';

export default function NuevaPropuesta() {
  const { usuario, tienePrivilegio } = useAuth();
  const navigate = useNavigate();
  const [categorias, setCategorias] = useState([]);
  const [categoriaSel, setCategoriaSel] = useState('');
  const [premioSel, setPremioSel] = useState('');
  const [candidatoPropio, setCandidatoPropio] = useState(true);
  const [candidatoNombre, setCandidatoNombre] = useState(usuario?.nombre_completo || '');
  const [resumen, setResumen] = useState('');
  const [documento, setDocumento] = useState(null);
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [convocatoriaActiva, setConvocatoriaActiva] = useState(true);

  useEffect(() => {
    api.get('/categorias-premio/', { params: { page_size: 100 } }).then((r) => {
      // Solo categorías y premios vigentes; los premios «por comisión» los asigna la comisión (RF-018/022).
      const puedeComision = tienePrivilegio('jefe_comision');
      const validas = (r.data.results || r.data)
        .filter((c) => c.activo)
        .map((c) => ({ ...c, premios: c.premios.filter((p) => p.activo && (puedeComision || !p.es_por_comision)) }))
        .filter((c) => c.premios.length);
      setCategorias(validas);
    });
    api.get('/publico/convocatoria-activa/').then((r) => setConvocatoriaActiva(r.data.convocatoria_activa));
  }, []);

  const bloqueado = !convocatoriaActiva && usuario?.rol === 'usuario';

  const categoria = categorias.find((c) => String(c.id) === String(categoriaSel));
  const premio = categoria?.premios.find((p) => String(p.id) === String(premioSel));

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (!premioSel || !resumen.trim()) {
      setError('Complete el premio y la fundamentación de la propuesta.');
      return;
    }
    const errorDoc = validarDocumento(documento);
    if (errorDoc) {
      setError(errorDoc);
      return;
    }
    setEnviando(true);
    try {
      const fd = new FormData();
      fd.append('premio', premioSel);
      fd.append('candidato_nombre', candidatoPropio ? usuario.nombre_completo : candidatoNombre);
      if (candidatoPropio) fd.append('candidato_usuario', usuario.id);
      fd.append('resumen', resumen);
      if (documento) fd.append('documento', documento);
      const { data } = await api.post('/propuestas/', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      navigate(`/app/propuestas/${data.id}`);
    } catch (err) {
      setError(mensajeError(err, 'No se pudo enviar la propuesta.'));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div>
      <div className="ph"><div><h2>Nueva Propuesta de Premio</h2><div className="phs">Convocatoria {new Date().getFullYear()}</div></div></div>
      <div className="ca" style={{ maxWidth: 700 }}>
        <div className="al-info"><span>📋</span><div>Puedes proponer candidatos para los premios de tu área. El jefe de departamento revisará y elevará tu propuesta.</div></div>
        {bloqueado && <div className="al-wn"><span>⏳</span><div>La convocatoria no está activa. Podrás subir propuestas cuando el administrador abra la etapa de convocatoria (consulta el calendario del proceso).</div></div>}
        {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
        <form onSubmit={handleSubmit}>
          <div className="card mb16">
            <div className="ch"><h3>Paso 1: Selección del Premio</h3></div>
            <div className="cb">
              <div className="fg2">
                <div className="fg">
                  <label className="req">Categoría</label>
                  <select className="fc" value={categoriaSel} onChange={(e) => { setCategoriaSel(e.target.value); setPremioSel(''); }} required>
                    <option value="">Seleccionar categoría...</option>
                    {categorias.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                  </select>
                </div>
                <div className="fg">
                  <label className="req">Premio</label>
                  <select className="fc" value={premioSel} onChange={(e) => setPremioSel(e.target.value)} required disabled={!categoria}>
                    <option value="">Seleccionar premio...</option>
                    {categoria?.premios.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                  </select>
                </div>
              </div>
              {premio && (
                <div className="card mt12" style={{ background: 'var(--light)', border: '1px solid rgba(0,51,102,.15)' }}>
                  <div className="cb">
                    <div style={{ fontWeight: 700, color: 'var(--blue)', marginBottom: 7 }}>📌 Criterios del Premio:</div>
                    <div style={{ fontSize: '.83rem', lineHeight: 1.75 }}>{premio.criterios || 'Sin criterios adicionales definidos.'}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card mb16">
            <div className="ch"><h3>Paso 2: Datos del Candidato</h3></div>
            <div className="cb">
              <div className="flex g8 mb12">
                <button type="button" className={candidatoPropio ? 'bp' : 'bs'} style={{ fontSize: '.8rem', padding: '6px 13px' }} onClick={() => setCandidatoPropio(true)}>👤 Proponer a mí mismo</button>
                <button type="button" className={!candidatoPropio ? 'bp' : 'bs'} style={{ fontSize: '.8rem', padding: '6px 13px' }} onClick={() => setCandidatoPropio(false)}>🔍 Proponer a otro trabajador</button>
              </div>
              {candidatoPropio ? (
                <div className="fg2">
                  <div className="fg"><label>Nombre y Apellidos</label><input className="fc" value={usuario?.nombre_completo || ''} readOnly /></div>
                  <div className="fg"><label>Área</label><input className="fc" value={usuario?.area_nombre || ''} readOnly /></div>
                </div>
              ) : (
                <div className="fg">
                  <label className="req">Nombre y Apellidos del candidato</label>
                  <input className="fc" value={candidatoNombre} onChange={(e) => setCandidatoNombre(e.target.value)} placeholder="Nombre completo o nombre del colectivo" required={!candidatoPropio} />
                </div>
              )}
            </div>
          </div>

          <div className="card mb16">
            <div className="ch"><h3>Paso 3: Fundamentación</h3></div>
            <div className="cb">
              <div className="fg mb12">
                <label className="req">Resumen de la propuesta</label>
                <textarea className="fc" rows={4} value={resumen} onChange={(e) => setResumen(e.target.value)} required
                  placeholder="Describa los méritos y resultados que fundamentan esta propuesta..." />
              </div>
              <div className="fg">
                <label>Documento de fundamentación (opcional)</label>
                <div className="uz" onClick={() => document.getElementById('doc-input').click()}>
                  <div style={{ fontSize: '1.6rem' }}>📎</div>
                  <div style={{ fontWeight: 600, fontSize: '.86rem', marginTop: 4 }}>{documento ? documento.name : 'Haz clic para adjuntar un archivo'}</div>
                  <div className="tsm tm" style={{ marginTop: 3 }}>PDF, DOC, DOCX u ODT — máx. 10 MB</div>
                </div>
                <input id="doc-input" type="file" accept=".pdf,.doc,.docx,.odt" hidden onChange={(e) => {
                  const archivo = e.target.files[0];
                  const problema = validarDocumento(archivo);
                  setError(problema);
                  setDocumento(problema ? null : archivo);
                }} />
              </div>
            </div>
          </div>

          <div className="flex g8">
            <button type="button" className="bs" style={{ padding: '10px 22px' }} onClick={() => navigate(-1)}>← Cancelar</button>
            <button type="submit" className="bp" style={{ flex: 1, justifyContent: 'center', padding: 10 }} disabled={enviando || bloqueado}>
              {enviando ? 'Enviando…' : '📤 Enviar Propuesta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
