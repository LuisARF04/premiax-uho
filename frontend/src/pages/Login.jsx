import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const CUENTAS_DEMO = [
  { username: 'cperez', rol: 'Superadmin' },
  { username: 'mrodriguez', rol: 'Admin' },
  { username: 'jpmartinez', rol: 'Gestor Global' },
  { username: 'rfuentes', rol: 'Jefe de Comisión (Formación de Pregrado)' },
  { username: 'agarcia', rol: 'Jefe de Área (Agronomía)' },
  { username: 'ltorres', rol: 'Jefe de Departamento (Biología)' },
  { username: 'pgomez', rol: 'Miembro de Comisión' },
  { username: 'rmedina', rol: 'Usuario' },
];

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('Premiax2025!');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setCargando(true);
    try {
      const usuario = await login(username, password);
      navigate(usuario.perfil_completo ? '/app/dashboard' : '/completar-perfil');
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo iniciar sesión.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg,#001F4D,#003366,#1A5276)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div style={{ background: '#fff', borderRadius: 16, padding: 38, maxWidth: 430, width: '100%', boxShadow: '0 20px 60px rgba(0,0,0,.3)' }}>
        <div style={{ textAlign: 'center', marginBottom: 26 }}>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.9rem', fontWeight: 900, color: 'var(--blue)' }}>
            PREMIAX<span style={{ color: 'var(--gold)' }}>·UHO</span>
          </div>
          <div style={{ fontSize: '.83rem', color: 'var(--muted)', marginTop: 4 }}>Sistema de Premios del Rector · UHO</div>
        </div>
        <div className="al-info"><span>ℹ️</span><div>Acceso exclusivo para <strong>trabajadores</strong> e <strong>instituciones</strong> con cuenta corporativa UHO (simulación de AGA_AUTH).</div></div>
        {error && <div className="al-re"><span>⚠️</span><div>{error}</div></div>}
        <form onSubmit={handleSubmit} style={{ border: '1.5px solid var(--border)', borderRadius: 10, padding: 18, background: 'var(--pale)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <div style={{ width: 34, height: 34, background: 'var(--blue)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 700, fontSize: '.82rem' }}>A</div>
            <div><div style={{ fontWeight: 700, fontSize: '.88rem' }}>AGA_AUTH</div><div style={{ fontSize: '.7rem', color: 'var(--muted)' }}>auth.uho.edu.cu (simulado)</div></div>
          </div>
          <div className="fg mb12">
            <label>Usuario</label>
            <input className="fc" list="cuentas-demo" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="usuario@uho.edu.cu" required />
            <datalist id="cuentas-demo">
              {CUENTAS_DEMO.map((c) => <option key={c.username} value={c.username}>{c.rol}</option>)}
            </datalist>
          </div>
          <div className="fg mb16">
            <label>Contraseña</label>
            <input className="fc" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="bp wf jc" style={{ padding: 11 }} type="submit" disabled={cargando}>
            {cargando ? 'Ingresando…' : '🔐 Iniciar Sesión con AGA_AUTH'}
          </button>
        </form>
        <div style={{ fontSize: '.74rem', color: 'var(--muted)', marginTop: 14 }}>
          Cuentas de demostración (contraseña <code>Premiax2025!</code>): {CUENTAS_DEMO.map((c) => c.username).join(', ')}.
        </div>
        <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)', textAlign: 'center' }}>
          <button className="bs" style={{ fontSize: '.8rem' }} onClick={() => navigate('/')}>← Volver al Sitio</button>
        </div>
      </div>
    </div>
  );
}
