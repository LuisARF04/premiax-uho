import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Loading } from '../components/ui';

const ETAPA_ESTADO_CLASE = { finalizada: 'done', en_curso: 'act', proxima: '' };
const ETAPA_ESTADO_LABEL = { finalizada: 'Finalizada', en_curso: 'En Curso', proxima: 'Próxima' };

export default function Landing() {
  const navigate = useNavigate();
  const [categorias, setCategorias] = useState(null);
  const [calendario, setCalendario] = useState(null);
  const [ganadores, setGanadores] = useState(null);
  const [anios, setAnios] = useState([]);
  const [anioSel, setAnioSel] = useState(null);
  const [convocatoriaActiva, setConvocatoriaActiva] = useState(false);
  const [reglamento, setReglamento] = useState(null);
  // Exclusivo para mostrar/ocultar el menú desplegable en móvil (Drawer); el punto de
  // corte real de cuándo aparece el botón lo decide la media query en index.css.
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    api.get('/publico/categorias/').then((r) => setCategorias(r.data));
    api.get('/publico/calendario/').then((r) => setCalendario(r.data));
    api.get('/publico/reglamento/').then((r) => setReglamento(r.data)).catch(() => setReglamento([]));
    api.get('/publico/convocatoria-activa/').then((r) => setConvocatoriaActiva(r.data.convocatoria_activa));
    api.get('/publico/ganadores/anios/').then((r) => {
      setAnios(r.data);
      if (r.data.length) setAnioSel(r.data[0]);
    });
  }, []);

  useEffect(() => {
    if (anioSel == null) return;
    api.get('/publico/ganadores/', { params: { anio: anioSel } }).then((r) => setGanadores(r.data));
  }, [anioSel]);

  const iconosCategoria = { ind_docente: '👩‍🏫', ind_no_docente: '👷', col_docente: '🏛️', col_no_docente: '🤝' };
  const coloresCategoria = { ind_docente: 'var(--blue)', ind_no_docente: 'var(--gold)', col_docente: 'var(--success)', col_no_docente: 'var(--danger)' };

  return (
    <div>
      <nav className="lnav">
        <div className="lnav-logo">PREMIAX<span>·UHO</span></div>
        <div className={`lnav-links${menuAbierto ? ' open' : ''}`} onClick={() => setMenuAbierto(false)}>
          <a className="lnav-lnk on" href="#inicio">Inicio</a>
          <a className="lnav-lnk" href="#reglamento">Reglamento</a>
          <a className="lnav-lnk" href="#premios">Premios</a>
          <a className="lnav-lnk" href="#galardonados">Galardonados</a>
          <a className="lnav-lnk" href="#calendario">Calendario</a>
        </div>
        <div className="lcta"><button className="btn-g" style={{ fontSize: '.8rem', padding: '8px 18px' }} onClick={() => navigate('/login')}>🏆 Proponer</button></div>
        <button className="lnav-toggle" onClick={() => setMenuAbierto((v) => !v)} aria-label="Abrir menú">{menuAbierto ? '✕' : '☰'}</button>
      </nav>

      <section className="hero" id="inicio">
        <div className="badge">✦ Convocatoria {new Date().getFullYear()} {convocatoriaActiva ? '— Activa' : ''}</div>
        <h1>Premios del <span>Rector</span><br />Universidad de Holguín</h1>
        <p>Sistema de Incentivos, Premiaciones y Atención al Hombre. Reconocemos la excelencia académica, científica y laboral de la comunidad universitaria.</p>
        <div className="cta-grp">
          <button className="btn-g" onClick={() => navigate('/login')}>🏆 Presentar Propuesta</button>
          <a className="btn-ow" href="#reglamento">📋 Ver Reglamento</a>
        </div>
        <div className="hero-stats">
          <div className="hstat"><div className="hstat-n">4</div><div className="hstat-l">Categorías</div></div>
          <div className="hstat"><div className="hstat-n">{categorias ? categorias.reduce((a, c) => a + c.premios.length, 0) : '…'}</div><div className="hstat-l">Tipos de Premio</div></div>
          <div className="hstat"><div className="hstat-n">{ganadores ? ganadores.length : '…'}</div><div className="hstat-l">Galardonados/año</div></div>
          <div className="hstat"><div className="hstat-n">15+</div><div className="hstat-l">Años de historia</div></div>
        </div>
      </section>

      <section className="sec wh" id="reglamento">
        <div className="sec-ttl">📋 Reglamento del Sistema</div>
        <div className="sec-sub">Principios y procedimiento del Sistema de Incentivos y Premiaciones de la UHO.</div>
        {!reglamento ? <Loading /> : (
          <div className="g3">
            {reglamento.map((sec, i) => (
              <div key={sec.id} style={{ background: 'var(--pale)', borderRadius: 'var(--r)', padding: 20, borderLeft: `4px solid ${['var(--blue)', 'var(--gold)', 'var(--success)'][i % 3]}` }}>
                <div style={{ fontSize: '1.4rem', marginBottom: 8 }}>{sec.icono}</div>
                <div style={{ fontWeight: 700, color: 'var(--blue)', marginBottom: 6 }}>{sec.titulo}</div>
                <div style={{ fontSize: '.84rem', color: 'var(--muted)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>{sec.contenido}</div>
              </div>
            ))}
            {!reglamento.length && <div className="tm">El reglamento aún no ha sido publicado.</div>}
          </div>
        )}
      </section>

      <section className="sec alt" id="calendario">
        <div className="sec-ttl">📅 Calendario del Proceso {new Date().getFullYear()}</div>
        <div className="sec-sub">Estado actual de las etapas de selección y otorgamiento de premios.</div>
        {!calendario ? <Loading /> : (
          <div className="tl">
            {calendario.map((e) => (
              <div key={e.id} className={`tli ${ETAPA_ESTADO_CLASE[e.estado]}`}>
                <div className="tld">{e.estado === 'finalizada' ? '✓' : e.estado === 'en_curso' ? '▶' : e.orden}</div>
                <div className="tll">{e.nombre}</div>
                <div className="tld2">{e.fecha_cierre}</div>
                <div className={`tls s-${e.estado === 'en_curso' ? 'act' : e.estado === 'finalizada' ? 'done' : 'next'}`}>{ETAPA_ESTADO_LABEL[e.estado]}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="sec wh" id="premios">
        <div className="sec-ttl">🏆 Categorías de Premios</div>
        <div className="sec-sub">Explora los premios disponibles por categoría y sus criterios de selección.</div>
        {!categorias ? <Loading /> : (
          <div className="cgrid">
            {categorias.map((c) => (
              <div className="ccard" key={c.id} style={{ borderTopColor: coloresCategoria[c.tipo] }}>
                <div className="cicon">{iconosCategoria[c.tipo]}</div>
                <div className="ctit">{c.nombre}</div>
                <div className="cct">{c.premios.length} tipos de premio</div>
                {c.premios.slice(0, 4).map((p) => (
                  <div className="ai" key={p.id}><div className="ad" /> {p.nombre}</div>
                ))}
                {c.premios.length > 4 && (
                  <div className="ai" style={{ color: 'var(--blue)', fontWeight: 600, border: 'none' }}>
                    <div className="ad" style={{ background: 'var(--blue)' }} /> Ver todos +{c.premios.length - 4} más...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="sec alt" id="galardonados">
        <div className="sec-ttl">🎖️ Galardonados</div>
        <div className="sec-sub">Reconocemos a los mejores trabajadores de la universidad.</div>
        <div className="ytabs">
          {anios.map((a) => (
            <div key={a} className={`ytab ${a === anioSel ? 'on' : ''}`} onClick={() => setAnioSel(a)}>{a}</div>
          ))}
        </div>
        {!ganadores ? <Loading /> : ganadores.length === 0 ? (
          <div className="empty-state">Aún no hay ganadores publicados para este año.</div>
        ) : (
          <div className="wgrid">
            {ganadores.map((g) => (
              <div className="wcard feat" key={g.id}>
                <div className="wavt">{(g.persona_nombre || '?').split(' ').slice(0, 2).map((w) => w[0]).join('')}</div>
                <div className="wname">{g.persona_nombre}</div>
                <div className="warea">{g.persona_area}{g.categoria_docente ? ` · ${g.categoria_docente}` : ''}</div>
                <div className="waw">{g.tipo === 'premio' ? '🏆' : '⭐'} {g.premio_nombre}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      <footer style={{ background: 'var(--blue)', color: 'rgba(255,255,255,.65)', padding: '24px 40px', textAlign: 'center', fontSize: '.81rem' }}>
        <strong style={{ color: '#fff', fontFamily: "'Playfair Display', serif" }}>PREMIAX-UHO</strong> · Sistema de Gestión de Premios del Rector · Universidad de Holguín © {new Date().getFullYear()}
      </footer>
    </div>
  );
}
