import { useState } from 'react';
import api from '../api/client';
import { PageHeader, Avatar } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function Perfil() {
  const { usuario, actualizarUsuario } = useAuth();
  const [prefs, setPrefs] = useState({
    notif_email: usuario.notif_email, notif_fechas_limite: usuario.notif_fechas_limite,
    notif_propuestas_elevadas: usuario.notif_propuestas_elevadas, notif_resumen_semanal: usuario.notif_resumen_semanal,
    foto_publica: usuario.foto_publica,
  });
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState('');

  async function guardar() {
    setGuardando(true);
    try {
      const { data } = await api.patch('/auth/me/', prefs);
      actualizarUsuario(data);
      setMensaje('Cambios guardados.');
      setTimeout(() => setMensaje(''), 2500);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div>
      <PageHeader title="Mi Perfil" subtitle="Información de tu cuenta en PREMIAX-UHO"
        actions={<button className="bp" onClick={guardar} disabled={guardando}>💾 Guardar cambios</button>} />
      <div className="ca" style={{ maxWidth: 680 }}>
        {mensaje && <div className="al-suc"><span>✅</span><div>{mensaje}</div></div>}
        <div className="card mb16">
          <div className="ch"><h3>👤 Datos Personales</h3><span className="bg bg-bl" style={{ marginLeft: 'auto' }}>Sincronizado con AGA_AUTH</span></div>
          <div className="cb">
            <div className="flex ic g12 mb16">
              <Avatar nombre={usuario.nombre_completo} size={72} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>{usuario.nombre_completo}</div>
                <div className="tsm tm">{usuario.email} · {usuario.tipo_aga}</div>
                <div style={{ marginTop: 5, display: 'flex', gap: 7 }}>
                  <span className="rc">{usuario.rol_display}</span>
                  <span className="bg bg-gr">Activo</span>
                </div>
              </div>
            </div>
            <div className="hr" />
            <div className="fg2">
              <div className="fg"><label>Nombre completo</label><input className="fc" value={usuario.nombre_completo} readOnly /></div>
              <div className="fg"><label>Correo institucional</label><input className="fc" value={usuario.email} readOnly /></div>
              <div className="fg"><label>Área</label><input className="fc" value={usuario.area_nombre || '—'} readOnly /></div>
              <div className="fg"><label>Departamento</label><input className="fc" value={usuario.departamento_nombre || '—'} readOnly /></div>
              <div className="fg"><label>Categoría Docente</label><input className="fc" value={usuario.categoria_docente_nombre || 'No aplica'} readOnly /></div>
              <div className="fg"><label>Categoría Científica</label><input className="fc" value={usuario.categoria_cientifica_nombre || 'No aplica'} readOnly /></div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="ch"><h3>⚙️ Preferencias de Notificación</h3></div>
          <div className="cb">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[
                ['notif_email', 'Notificaciones por correo'],
                ['notif_fechas_limite', 'Alertas de fecha límite próxima'],
                ['notif_propuestas_elevadas', 'Notificaciones de propuestas elevadas'],
                ['notif_resumen_semanal', 'Resumen semanal del proceso'],
                ['foto_publica', 'Mostrar mi foto en el landing page (RF/protección de datos)'],
              ].map(([key, label]) => (
                <div className="flex ic" style={{ justifyContent: 'space-between' }} key={key}>
                  <span style={{ fontSize: '.86rem' }}>{label}</span>
                  <input type="checkbox" checked={prefs[key]} onChange={(e) => setPrefs({ ...prefs, [key]: e.target.checked })} style={{ width: 18, height: 18, cursor: 'pointer' }} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
